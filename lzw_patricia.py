import sys
import struct
import time
import os
import csv

# ==========================================
# TASK 3: PATRICIA TRIE (RADIX TREE)
# ==========================================

class PatriciaNode:
    def __init__(self, code=-1):
        self.code = code
        # Dictionary mapping: first_byte (int) -> (label_bytes, child_node)
        self.edges = {}

class PatriciaDictionary:
    def __init__(self):
        self.root = PatriciaNode()
        self.num_entries = 0
        self.next_code = 256
        
        # Initialize ASCII 0-255
        # In a Patricia Trie, these are just 256 edges coming off the root
        for i in range(256):
            char = bytes([i])
            self.insert(char, i)
        
    def insert(self, string, code):
        """
        Inserts a string with a specific code into the Patricia Trie.
        Handles edge splitting if a divergence occurs in the middle of a label.
        """
        node = self.root
        idx = 0
        n = len(string)
        
        while idx < n:
            char = string[idx]
            
            # Case 1: No edge starts with this character
            if char not in node.edges:
                # Create a new edge for the *rest* of the string
                remaining_label = string[idx:]
                new_child = PatriciaNode(code)
                node.edges[char] = (remaining_label, new_child)
                self.num_entries += 1
                return True
            
            # Case 2: Edge exists, traverse it
            label, child = node.edges[char]
            
            # Find the length of the common prefix between (string[idx:]) and (label)
            j = 0
            while j < len(label) and idx + j < n and label[j] == string[idx + j]:
                j += 1
            
            # 'j' is the matching length
            
            if j == len(label):
                # Full match on the edge label. 
                # Move down to the child and continue
                idx += j
                node = child
                
                # If we reached the end of the string, update the code (if strictly updating)
                if idx == n:
                    if node.code == -1:
                        node.code = code
                        self.num_entries += 1
                        return True
                    else:
                        return False # Already exists
            else:
                # Partial match! Divergence happens inside the edge.
                # We must SPLIT the edge.
                # Existing edge: label -> child
                # Split at index 'j'. 
                
                # 1. Create the 'split' node
                split_node = PatriciaNode() # No code yet (unless string ends here)
                
                # 2. The common part becomes the label to the split node
                common_part = label[:j]
                
                # 3. The remaining part of the OLD label goes to the old child
                rest_of_old_label = label[j:]
                split_node.edges[rest_of_old_label[0]] = (rest_of_old_label, child)
                
                # 4. The remaining part of the NEW string goes to a new child
                rest_of_new_string = string[idx+j:]
                
                if not rest_of_new_string:
                    # The new string ended exactly at the split
                    split_node.code = code
                else:
                    new_leaf = PatriciaNode(code)
                    split_node.edges[rest_of_new_string[0]] = (rest_of_new_string, new_leaf)
                
                # 5. Connect parent (node) to the split_node
                node.edges[char] = (common_part, split_node)
                
                self.num_entries += 1
                return True
        return False

    def search_longest_prefix(self, string):
        """
        Finds the longest prefix of 'string' that exists in the dictionary.
        Returns (node_code, match_length)
        """
        node = self.root
        idx = 0
        n = len(string)
        last_valid_code = -1
        last_valid_len = 0
        
        while idx < n:
            char = string[idx]
            
            if char not in node.edges:
                break
                
            label, child = node.edges[char]
            
            # Check how much of the label matches the input string
            j = 0
            while j < len(label) and idx + j < n and label[j] == string[idx + j]:
                j += 1
            
            if j == len(label):
                # Full edge matched
                idx += j
                node = child
                if node.code != -1:
                    last_valid_code = node.code
                    last_valid_len = idx
            else:
                # Partial edge match - we can't go further
                break
                
        return last_valid_code, last_valid_len

    def size(self):
        return self.num_entries

    def dump_to_csv(self, filename):
        rows = []
        def dfs(node, current_str):
            if node.code != -1:
                rows.append((node.code, current_str))
            for char_key in node.edges:
                label, child = node.edges[char_key]
                dfs(child, current_str + label)
        
        dfs(self.root, b"")
        rows.sort(key=lambda x: x[0])
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Code", "String (Repr)"])
                for code, s in rows:
                    writer.writerow([code, repr(s)])
            print(f"[Log] Dictionary dumped to {filename}")
        except:
            pass

# ==========================================
# COMPRESSOR (PATRICIA VERSION)
# ==========================================

def lzw_compress_patricia(input_path, output_path, csv_path):
    print(f"--- Starting Patricia Compression: {input_path} ---")
    
    dictionary = PatriciaDictionary()
    
    start_time = time.time()
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except:
        return

    if not data:
        return

    compressed_codes = []
    
    # LZW Logic with Patricia Search
    # Unlike basic Trie, we can't just hold a node pointer because 
    # the "longest match" might cover multiple edges or part of an edge.
    # We will use the 'search_longest_prefix' helper.
    
    idx = 0
    n = len(data)
    
    while idx < n:
        # We want to match the longest string starting at data[idx]
        # We can look ahead safely because we have the whole data in memory
        
        # Heuristic: We only need to peek ahead as much as the longest likely string.
        # But 'search_longest_prefix' handles limits naturally.
        
        # 1. Find longest match P
        # We pass a slice of the data. In production, avoid slicing large buffers.
        # For this project, slicing is fine.
        remainder = data[idx:] 
        code, match_len = dictionary.search_longest_prefix(remainder)
        
        # P is data[idx : idx + match_len]
        
        # 2. Output code for P
        compressed_codes.append(code)
        
        # 3. Add P + C to dictionary
        # P + C is data[idx : idx + match_len + 1]
        if idx + match_len < n:
            new_string = data[idx : idx + match_len + 1]
            if dictionary.next_code < 65536:
                dictionary.insert(new_string, dictionary.next_code)
                dictionary.next_code += 1
        
        # 4. Advance
        idx += match_len
        
        if idx % 1000 == 0:
             sys.stdout.write(f"\rCompressing: {idx}/{n} bytes")
             sys.stdout.flush()

    print(f"\rCompressing: {n}/{n} bytes - Done.")

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
    
    print("\n[Patricia Compression Metrics]")
    print(f"Time Taken: {duration:.4f} seconds")
    print(f"Original Size: {input_size} bytes")
    print(f"Compressed Size: {output_size} bytes")
    print(f"Compression Ratio: {compression_ratio:.2f}")
    print(f"Throughput: {throughput:.2f} MB/s")
    print(f"Peak Dictionary Size: {dictionary.size()} entries")
    
    dictionary.dump_to_csv(csv_path)

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    test_input = "test_synthetic.txt"
    # We use the same decompressor logic (standard LZW rule)
    from lzw_trie import lzw_decompress_standard
    
    compressed_file = "test_output_patricia.lzw"
    decompressed_file = "test_restored_patricia.txt"
    comp_csv = "dict_patricia_compressor.csv"
    decomp_csv = "dict_patricia_decompressor.csv"

    # 1. Compress
    lzw_compress_patricia(test_input, compressed_file, comp_csv)
    
    # 2. Decompress (Reuse Task 2/1 logic)
    lzw_decompress_standard(compressed_file, decompressed_file, decomp_csv)
    
    # 3. Verification
    print("\n--- Verification ---")
    if os.path.exists(test_input) and os.path.exists(decompressed_file):
        with open(test_input, 'rb') as f1, open(decompressed_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("SUCCESS: Decompressed file matches original exactly!")
            else:
                print("FAILURE: Files do not match.")