#!/usr/bin/env python3
#
# Duplicate Directory Finder
# Licensed under the MIT License. See LICENSE file for details.
#
import os
import hashlib
import sys
import shutil
from collections import defaultdict

# Directories to skip entirely during all traversals
IGNORED_DIRS = {'.git', '.local', '.cache', '.config', '.nvm', '.joplin-bin', 'venv', '.vim'}

# Global cache to avoid re-hashing the same file multiple times
# Key: absolute path, Value: (mtime, size, hash)
FILE_HASH_CACHE = {}

def get_file_hash(filepath):
    """Calculates the SHA-256 hash of a file with caching."""
    try:
        # Dangling symlinks can't be read; hash the target path instead so they
        # are included in directory signatures rather than silently dropped.
        if os.path.islink(filepath) and not os.path.exists(filepath):
            target = os.readlink(filepath)
            return hashlib.sha256(f"SYMLINK:{target}".encode()).hexdigest()

        stat = os.stat(filepath)
        cache_key = os.path.abspath(filepath)
        
        # If file hasn't changed, return cached hash
        if cache_key in FILE_HASH_CACHE:
            mtime, size, file_hash = FILE_HASH_CACHE[cache_key]
            if mtime == stat.st_mtime and size == stat.st_size:
                return file_hash
        
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(128 * 1024): # 128KB chunks
                sha256.update(chunk)
        
        file_hash = sha256.hexdigest()
        FILE_HASH_CACHE[cache_key] = (stat.st_mtime, stat.st_size, file_hash)
        return file_hash
    except (OSError, IOError):
        return None

def get_dir_metadata(dir_path):
    """
    Returns a 'cheap' signature (paths and sizes) and a list of absolute file paths.
    Used for first-pass filtering.
    """
    metadata = []
    abs_paths = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dir_path)
            try:
                if os.path.islink(full_path) and not os.path.exists(full_path):
                    # Dangling symlink: os.path.getsize would raise OSError.
                    # Use the symlink's own lstat size (length of target string).
                    size = os.lstat(full_path).st_size
                else:
                    size = os.path.getsize(full_path)
                metadata.append((rel_path, size))
                abs_paths.append(full_path)
            except OSError:
                continue
    
    metadata.sort()
    # Create a string representation of the metadata for grouping
    meta_sig = "|".join(f"{p}:{s}" for p, s in metadata)
    return hashlib.md5(meta_sig.encode()).hexdigest(), abs_paths, len(metadata)

def get_full_dir_signature(dir_path):
    """
    Generates the final 'expensive' signature using file hashes.
    """
    files_info = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dir_path)
            file_hash = get_file_hash(full_path)
            if file_hash:
                files_info.append((rel_path, file_hash))
    
    files_info.sort()
    full_sig_content = "|".join(f"{p}:{h}" for p, h in files_info)
    return hashlib.sha256(full_sig_content.encode()).hexdigest()

def find_duplicates(root_search_path):
    # Step 1: Group by cheap metadata
    cheap_groups = defaultdict(list)
    
    print(f"Scanning {root_search_path}...")
    all_dirs = []
    for root, dirs, _ in os.walk(root_search_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for d in dirs:
            all_dirs.append(os.path.join(root, d))
    
    total = len(all_dirs)
    for idx, dir_path in enumerate(all_dirs):
        if (idx + 1) % 100 == 0 or (idx + 1) == total:
            print(f"\rStep 1/2: Metadata scan {idx + 1}/{total}...", end="", flush=True)
        
        meta_sig, _, file_count = get_dir_metadata(dir_path)
        if file_count > 0:
            cheap_groups[meta_sig].append(dir_path)
    
    # Step 2: For groups with > 1 dir, verify with hashes
    print("\nStep 2/2: Verifying matches with file hashes...")
    final_duplicates = defaultdict(list)
    
    potential_sets = [paths for paths in cheap_groups.values() if len(paths) > 1]
    for paths in potential_sets:
        # Group these specific paths by their full hash-based signature
        sub_groups = defaultdict(list)
        for p in paths:
            full_sig = get_full_dir_signature(p)
            sub_groups[full_sig].append(p)
        
        for sig, matched_paths in sub_groups.items():
            if len(matched_paths) > 1:
                # Calculate size once for the set
                size = 0
                count = 0
                for r, dirs, files in os.walk(matched_paths[0]):
                    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                    size += sum(os.lstat(os.path.join(r, f)).st_size for f in files)
                    count += len(files)
                final_duplicates[sig] = {
                    'paths': matched_paths,
                    'size': size,
                    'count': count
                }

    # Convert to list and sort by size
    result = list(final_duplicates.values())
    result.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"Found {len(result)} sets of duplicate directories.\n")
    return result

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def prompt_deletion(duplicates):
    if not duplicates:
        print("No duplicate directories found.")
        return

    set_count = len(duplicates)
    for i, dup_set in enumerate(duplicates, 1):
        paths = [p for p in dup_set['paths'] if os.path.exists(p)]
        if len(paths) <= 1: continue
            
        print("-" * 40)
        print(f"Set {i}/{set_count}: {dup_set['count']} files, total size: {format_size(dup_set['size'])}")
        for j, path in enumerate(paths):
            print(f"[{j}] {path}")
        
        while True:
            paths = [p for p in paths if os.path.exists(p)]
            if len(paths) <= 1: break
                
            choice = input("\nDelete index (or 's' skip, 'q' quit): ").lower()
            if choice == 'q': return
            if choice == 's': break
            
            try:
                idx = int(choice)
                if 0 <= idx < len(paths):
                    target = paths[idx]
                    if input(f"Confirm deletion of '{target}'? (yes/no): ").lower() == 'yes':
                        shutil.rmtree(target)
                        print("Deleted.")
                        paths = [p for p in paths if os.path.exists(p)]
                        if len(paths) <= 1: break
                        print("\nRemaining:")
                        for j, path in enumerate(paths): print(f"[{j}] {path}")
                else:
                    print("Invalid index.")
            except ValueError:
                print("Enter a number, 's', or 'q'.")

if __name__ == "__main__":
    search_path = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.isdir(search_path):
        print(f"Error: {search_path} is not a directory.")
        sys.exit(1)
        
    dups = find_duplicates(search_path)
    prompt_deletion(dups)
