import os
import time
import xxhash
import argparse
from natsort import natsorted

# Default exclusions list - files matching these patterns will be skipped
EXCLUSIONS = [
    ".*",          
    "README.md",
    "LICENSE"
              
]

def hash_file_xxhash_full(filepath, chunk_size=1024 * 1024):
    # full hash with 1MB chunk
    h = xxhash.xxh3_64()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()

def hash_file_xxhash_partial(filepath, chunk_size=1024 * 1024, max_chunks=25):
    # partial hash of first(file max_chunks * 1MB)
    # good for large files
    
    h = xxhash.xxh3_64()
    chunks_processed = 0
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
            chunks_processed += 1
            if chunks_processed >= max_chunks:
                break
    
    return h.hexdigest()

def should_exclude(filename, exclusions=EXCLUSIONS):
    """Check if a file should be excluded based on patterns."""
    # For dot files pattern
    if ".*" in exclusions and os.path.basename(filename).startswith('.'):
        return True
        
    # For exact matches
    if os.path.basename(filename) in exclusions:
        return True
        
    return False

def hash_single_file(file_path, hash_mode="full", max_chunks=10):
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a file.")
        return None
    
    total_start = time.perf_counter()
    
    if hash_mode == "full":
        hash_value = hash_file_xxhash_full(file_path)
    elif hash_mode == "partial":
        hash_value = hash_file_xxhash_partial(file_path, max_chunks=max_chunks)
    else:
        print(f"Error: Invalid hash mode '{hash_mode}'")
        return None
        
    total_time = time.perf_counter() - total_start
    
    return hash_value, total_time

def hash_all_files(entries, target_dir, hash_mode="full", max_chunks=10, exclusions=EXCLUSIONS):
    total_start = time.perf_counter()
    file_hashes = []
    excluded_count = 0

    for entry in entries:
        path = os.path.join(target_dir, entry)
        
        # Skip this file if it matches exclusion patterns
        if should_exclude(path, exclusions):
            excluded_count += 1
            continue
            
        if os.path.isfile(path):
            if hash_mode == "full":
                hash_value = hash_file_xxhash_full(path)
            elif hash_mode == "partial":
                hash_value = hash_file_xxhash_partial(path, max_chunks=max_chunks)
            
            file_hashes.append((path, hash_value))

    total_time = time.perf_counter() - total_start
    return file_hashes, total_time, excluded_count

def main():
    parser = argparse.ArgumentParser(description="Calculate xxHash for files in directory.")
    parser.add_argument('--dir_path', type=str, default='.', help="Directory to hash (default: current directory)")
    parser.add_argument('--file_path', type=str, help="Single file to hash (overrides dir_path if specified)")
    parser.add_argument('--hash_mode', type=str, choices=["full", "partial"], default="full", 
                        help="Hashing mode - full or partial (default: full)")
    parser.add_argument('--max_chunks', type=int, default=25, 
                        help="Maximum chunks to read for partial hashing (default: 25)")
    args = parser.parse_args()

    # Print exclusions
    print("Excluding files matching:")
    for excl in EXCLUSIONS:
        print(f"  - {excl}")
    print()

    # single file 
    # If file_path is provided, only hash that file
    if args.file_path:
        file_path = os.path.abspath(args.file_path)
        
        # Check if this file should be excluded
        if should_exclude(file_path):
            print(f"Skipping excluded file: {file_path}")
            return
            
        print(f"Hashing single file: {file_path}")
        print(f"Hash mode: {args.hash_mode}")
        
        if args.hash_mode == "partial":
            print(f"Max chunks: {args.max_chunks}")
        
        result = hash_single_file(file_path, hash_mode=args.hash_mode, max_chunks=args.max_chunks)
        if result:
            hash_value, hash_time = result
            print(f"File: {os.path.basename(file_path)}")
            print(f"Hash: {hash_value}")
            print(f"Time: {hash_time:.6f} seconds")
        return

    # dir 
    # Otherwise hash all files in the directory
    target_dir = os.path.abspath(args.dir_path)
    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a directory.")
        return

    entries = natsorted(os.listdir(target_dir))
    # Filter to only include files (not directories)
    entries = [e for e in entries if os.path.isfile(os.path.join(target_dir, e))]
    total_files = len(entries)

    print(f"Found {total_files} files in: {target_dir}")
    print(f"Hash mode: {args.hash_mode}")
    
    if args.hash_mode == "partial":
        print(f"Max chunks: {args.max_chunks}")
    
    print("\nRunning xxHash pass...")
    file_hashes, xx_time, excluded_count = hash_all_files(entries, target_dir, 
                                                         hash_mode=args.hash_mode, 
                                                         max_chunks=args.max_chunks)
    
    print("\nFile Hashes:")
    for file_path, hash_value in file_hashes:
        print(f"{hash_value} : {os.path.basename(file_path)}")
    
    print(f"\nxxHash total time: {xx_time:.6f} seconds")
    print(f"Files processed: {len(file_hashes)}")
    print(f"Files excluded: {excluded_count}")

if __name__ == "__main__":
    main()