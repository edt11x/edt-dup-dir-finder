# Duplicate Directory Finder

A fast, memory-efficient Python utility to find and manage duplicate directories on Linux systems.

## Features

- **Content-Based Matching**: Identifies duplicates by comparing relative file paths, file sizes, and SHA-256 hashes.
- **Timestamp Independent**: Correctly identifies duplicate directories even if their file modification dates are different.
- **Two-Stage Verification**: 
    1. **Metadata Scan**: Quickly groups directories by file structure and sizes.
    2. **Hash Verification**: Only performs intensive SHA-256 hashing on potential matches, making it suitable for thousands of directories.
- **Global File Hashing Cache**: Prevents re-hashing the same file multiple times during a scan.
- **Safe Management**: 
    - Interactive CLI prompts for deletion.
    - Double-confirmation before any files are removed.
    - Automatically handles nested duplicates (cleans up references if a parent is deleted).
- **Informed Deletion**: Displays total file count and data size for each duplicate set.

## Installation

The app uses a Python virtual environment to keep your system clean.

1. **Run the setup script**:
   ```bash
   ./setup.sh
   ```
   *This will create a `venv` directory and install any necessary requirements.*

2. **Activate the environment**:
   ```bash
   source venv/bin/activate
   ```

## Usage

Run the script by passing the directory you want to scan:

```bash
python3 dup_dir_finder.py /path/to/search
```

### Reviewing Results

The app will list duplicate sets starting with the largest first:

```text
Found 3 sets of duplicate directories.

----------------------------------------
Set 1/3: 150 files, total size: 1.42 GB
Found 2 duplicate directories:
[0] /home/user/backups/photos_v1
[1] /home/user/backups/photos_copy

Delete index (or 's' skip, 'q' quit): 
```

1. **Delete**: Enter the number (e.g., `0`) to delete that directory.
2. **Skip**: Enter `s` to move to the next set of duplicates.
3. **Quit**: Enter `q` to exit the application.

## Requirements

- Python 3.x
- Linux environment (tested on Ubuntu/Debian/Fedora)

## File Structure

- `dup_dir_finder.py`: The main application script.
- `setup.sh`: Environment setup script.
- `requirements.txt`: Python dependency list.
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
