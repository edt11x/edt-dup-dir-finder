#!/bin/bash
# create_test_data.sh - Generates test directories for duplicate detection

BASE_DIR="test_data"
mkdir -p "$BASE_DIR"

# 1. Create a base directory
mkdir -p "$BASE_DIR/dir_a"
echo "hello world" > "$BASE_DIR/dir_a/file1.txt"
echo "duplicate content" > "$BASE_DIR/dir_a/file2.txt"
mkdir -p "$BASE_DIR/dir_a/subdir"
echo "nested" > "$BASE_DIR/dir_a/subdir/nested.txt"

# 2. Create an exact duplicate (dir_b)
cp -r "$BASE_DIR/dir_a" "$BASE_DIR/dir_b"
touch -d "2020-01-01" "$BASE_DIR/dir_b/file1.txt" # Change timestamp

# 3. Create a directory with same files but different content (dir_c)
cp -r "$BASE_DIR/dir_a" "$BASE_DIR/dir_c"
echo "different content" > "$BASE_DIR/dir_c/file1.txt"

# 4. Create a directory with same content but different filename (dir_d)
mkdir -p "$BASE_DIR/dir_d"
echo "hello world" > "$BASE_DIR/dir_d/different_name.txt"
echo "duplicate content" > "$BASE_DIR/dir_d/file2.txt"
mkdir -p "$BASE_DIR/dir_d/subdir"
echo "nested" > "$BASE_DIR/dir_d/subdir/nested.txt"

# 5. Create a directory that is a subset (dir_e)
mkdir -p "$BASE_DIR/dir_e"
echo "hello world" > "$BASE_DIR/dir_e/file1.txt"

echo "Test data created in $BASE_DIR"
