import sys
import struct
import time
import os
import csv

# ==========================================
# TASK 2: TRIE-BASED DICTIONARY
# ==========================================

class TrieNode:
    def __init__(self, code=-1):
        self.code = code
        self.children = {}  # Map: char (byte) -> TrieNode

class TrieDictionary:
    def __init__(self):
        self.root = TrieNode()
        self.next_code = 0
        self.num_entries = 0
        
        # Initialize with ASCII 0-255
        for i in range(256):
            self.insert_initial(bytes([i]), i)
        self.next_code = 256

    def insert_initial(self, string, code):
        """Helper to load ASCII table initially."""
        node = self.root
        for byte in string:
            if byte not in node.children:
                node.children[byte] = TrieNode()
            node = node.children[byte]
        node.code = code
        self.num_entries += 1

    def search_node(self, byte_val, current_node):
        """
        Fast lookup: Checks if 'current_node' has a child 'byte_val'.
        Returns the child node if exists, else None.
        """
        return current_node.children.get(byte_val)

    def insert_child(self, byte_val, parent_node):
        """
        Adds a new node as a child of parent_node with the next available code.
        """
        if self.next_code < 65536:
            new_node = TrieNode(self.next_code)
            parent_node.children[byte_val] = new_node
            self.next_code += 1
            self.num_entries += 1
            return True
        return False

    def size(self):
        return self.num_entries

    def dump_to_csv(self, filename):
        """
        Traverses the Trie to verify dictionary content. 
        Uses DFS to reconstruct strings.
        """
        rows = []
        def dfs(node, path_bytes):
            if node.code != -1:
                rows.append((node.code, path_bytes))
            for byte_val, child in node.children.items():
                dfs(child, path_bytes + bytes([byte_val]))
        
        dfs(self.root, b"")
        # Sort by code for readability
        rows.sort(key=lambda x: x[0])
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Code", "String (Repr)"])
                for code, string in rows:
                    writer.writerow([code, repr(string)])
            print(f"[Log] Dictionary dumped to {filename}")
        except Exception as e:
            print(f"[Error] Could not dump dictionary: {e}")

# ==========================================
# COMPRESSOR (TRIE VERSION)
# ==========================================

def lzw_compress_trie(input_path, output_path, csv_path):
    print(f"--- Starting Trie Compression: {input_path} ---")
    
    dictionary = TrieDictionary()
    
    start_time = time.time()
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("Input file not found.")
        return

    if not data:
        return

    compressed_codes = []
    
    # --- TRIE OPTIMIZATION LOGIC ---
    # Instead of string concatenation P + C, we maintain a pointer 'curr_node'
    
    # Start with the first character
    first_byte = data[0]
    # In a fresh trie, the first byte (ASCII) definitely exists at root's children
    curr_node = dictionary.root.children[first_byte]
    
    total_bytes = len(data)
    
    for i in range(1, total_bytes):
        byte_val = data[i]
        
        # Check if we can walk down the tree
        next_node = dictionary.search_node(byte_val, curr_node)
        
        if next_node is not None:
            # Match found (P + C exists)
            # Move pointer down
            curr_node = next_node
        else:
            # No match (P + C does not exist)
            
            # 1. Output code for Current Node (P)
            compressed_codes.append(curr_node.code)
            
            # 2. Add New Child (P + C) to Trie
            dictionary.insert_child(byte_val, curr_node)
            
            # 3. Reset: Start search from Root -> C
            # Since we know single chars (ASCII) are always in dict:
            curr_node = dictionary.root.children[byte_val]

        if i % 50000 == 0:
             sys.stdout.write(f"\rCompressing: {i}/{total_bytes} bytes")
             sys.stdout.flush()

    # Output the straggler
    compressed_codes.append(curr_node.code)
    
    print(f"\rCompressing: {total_bytes}/{total_bytes} bytes - Done.")

    # Write output
    with open(output_path, 'wb') as f:
        for code in compressed_codes:
            f.write(struct.pack('>H', code))

    end_time = time.time()
    duration = end_time - start_time
    input_size = os.path.getsize(input_path)
    output_size = os.path.getsize(output_path)
    compression_ratio = input_size / output_size if output_size > 0 else 0
    throughput = (input_size / 1024 / 1024) / duration if duration > 0 else 0
    
    print("\n[Trie Compression Metrics]")
    print(f"Time Taken: {duration:.4f} seconds")
    print(f"Original Size: {input_size} bytes")
    print(f"Compressed Size: {output_size} bytes")
    print(f"Compression Ratio: {compression_ratio:.2f}")
    print(f"Throughput: {throughput:.2f} MB/s")
    print(f"Peak Dictionary Size: {dictionary.size()} entries")
    
    dictionary.dump_to_csv(csv_path)

# ==========================================
# DECOMPRESSOR (STANDARD ARRAY)
# ==========================================
# Note: Decompression maps Code -> String. An array is O(1). 
# A Trie is not algorithmically beneficial for the decompressor's lookups.
# We reuse the logic from Task 1 for the Decompressor to ensure correctness.

def lzw_decompress_standard(input_path, output_path, csv_path):
    print(f"\n--- Starting Decompression: {input_path} ---")
    
    # Initialize Standard List Dictionary
    dictionary = [bytes([i]) for i in range(256)]
    
    start_time = time.time()
    
    decompressed_data = bytearray()
    
    try:
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
    except FileNotFoundError:
        return

    codes = []
    for i in range(0, len(compressed_data), 2):
        chunk = compressed_data[i:i+2]
        if len(chunk) == 2:
            codes.append(struct.unpack('>H', chunk)[0])

    if not codes:
        return

    OLD_CODE = codes[0]
    OLD_STRING = dictionary[OLD_CODE]
    decompressed_data.extend(OLD_STRING)
    
    for i in range(1, len(codes)):
        NEW_CODE = codes[i]
        
        if NEW_CODE < len(dictionary):
            STRING = dictionary[NEW_CODE]
        elif NEW_CODE == len(dictionary):
            STRING = OLD_STRING + bytes([OLD_STRING[0]])
        else:
            raise ValueError("Bad compressed code")
        
        decompressed_data.extend(STRING)
        
        # Add to dictionary
        dictionary.append(OLD_STRING + bytes([STRING[0]]))
        
        OLD_CODE = NEW_CODE
        OLD_STRING = STRING

    with open(output_path, 'wb') as f:
        f.write(decompressed_data)

    end_time = time.time()
    print(f"[Decompression Metrics] Time: {end_time - start_time:.4f}s")
    
    # Dump Dictionary to CSV
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Code", "String (Repr)"])
            for code, entry in enumerate(dictionary):
                writer.writerow([code, repr(entry)])
    except:
        pass

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    test_input = "test_synthetic.txt"
    compressed_file = "test_output_trie.lzw"
    decompressed_file = "test_restored_trie.txt"
    comp_csv = "dict_trie_compressor.csv"
    decomp_csv = "dict_trie_decompressor.csv"

    # 1. Compress with Trie
    lzw_compress_trie(test_input, compressed_file, comp_csv)
    
    # 2. Decompress
    lzw_decompress_standard(compressed_file, decompressed_file, decomp_csv)
    
    # 3. Verification
    print("\n--- Verification ---")
    if os.path.exists(test_input) and os.path.exists(decompressed_file):
        with open(test_input, 'rb') as f1, open(decompressed_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("SUCCESS: Decompressed file matches original exactly!")
            else:
                print("FAILURE: Files do not match.")