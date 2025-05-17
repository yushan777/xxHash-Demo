# xxHash-Demo

A Python script for calculating xxHash checksums of files.

## Features

- Fast xxHash3_64 algorithm implementation
- Two hashing modes: full or partial file (first X MB)
- Single file or directory batch processing
- File exclusion patterns

Install dependencies with:
```
pip install xxhash natsort
```

### Basic Usage

Hash a single file:
```
python hash.py --file_path /path/to/file
```

Hash all files in a directory:
```
python hash.py --dir_path /path/to/directory
```

### Advanced Options

Partial hashing (first 1MB * max_chunks (default 25) of each file):
```
python hash.py --dir_path /path/to/directory --hash_mode partial
```

Customize the chunk limit for partial hashing:
```
python hash.py --file_path /path/to/largefile --hash_mode partial --max_chunks 20
```

## Exclusion Patterns

By default, the script excludes:
- Hidden files (with names starting with `.`)
- The README.md file

To modify exclusions, edit the `EXCLUSIONS` list at the top of the script.

## Output Format

For single files:
```
Hashing single file: /path/to/file
Hash mode: full
File: filename.ext
Hash: a1b2c3d4e5f6...
Time: 0.123456 seconds
```

For directories:
```
Hashing 42 files in: /path/to/directory
Hash mode: full

Running xxHash pass...

File Hashes:
a1b2c3d4e5f6... : file1.txt
fedcba987654... : file2.bin

xxHash total time: 1.234567 seconds
Files processed: 40
Files excluded: 2
```

## Performance

xxHash is extremely fast, especially compared to cryptographic hash functions like SHA256. The partial hashing mode is particularly useful for large files when a full content hash is not required.
