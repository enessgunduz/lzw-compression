import random
import os

def create_genome_file(filename, size_mb=1):
    """
    Generates a file simulating DNA sequences (A, C, G, T).
    Genome data is repetitive but has high entropy (randomness) within the 4 chars.
    """
    print(f"Generating Genome file: {filename} ({size_mb} MB)...")
    bases = ['A', 'C', 'G', 'T']
    
    # 1 MB = 1024 * 1024 bytes
    target_size = size_mb * 1024 * 1024
    
    with open(filename, 'w') as f:
        # Write in chunks to be efficient
        chunk_size = 1024
        bytes_written = 0
        while bytes_written < target_size:
            # Create a chunk of random bases
            chunk = ''.join(random.choices(bases, k=chunk_size))
            f.write(chunk)
            bytes_written += len(chunk)
    
    print("Done.")

def create_synthetic_file(filename, size_mb=1):
    """
    Generates highly repetitive synthetic data.
    Excellent for testing best-case compression ratio
    Pattern: AAAAA...BBBBB... repeated.
    """
    print(f"Generating Synthetic file: {filename} ({size_mb} MB)...")
    target_size = size_mb * 1024 * 1024
    
    with open(filename, 'w') as f:
        bytes_written = 0
        while bytes_written < target_size:
            # High repetition: 1000 As followed by 1000 Bs
            chunk = "A" * 1000 + "B" * 1000 + "C" * 500
            f.write(chunk)
            bytes_written += len(chunk)
    print("Done.")

def create_source_code_file(filename):
    """
    Combines the existing Python scripts into one file to simulate 'Source Code' input.
    Source code has medium repetition (keywords like 'def', 'import', 'self').
    """
    print(f"Generating Source Code file: {filename}...")
    source_files = ["lzw_array.py", "lzw_trie.py", "lzw_patricia.py"]
    
    with open(filename, 'w', encoding='utf-8') as outfile:
        for fname in source_files:
            if os.path.exists(fname):
                outfile.write(f"\n# --- CONTENT OF {fname} ---\n")
                with open(fname, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            else:
                print(f"Warning: {fname} not found (skipping).")
    print("Done.")

if __name__ == "__main__":
    # 1. Genome File (1MB is large enough to see speed differences)
    create_genome_file("test_genome.txt", size_mb=1)
    
    # 2. Synthetic File (1MB)
    create_synthetic_file("test_synthetic.txt", size_mb=1)
    
    # 3. Source Code File
    create_source_code_file("test_source.txt")