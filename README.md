CSE 4077 Project 1: LZW Encoder-Decoder
=======================================

Project Overview
----------------

This project implements a complete **Lempel-Ziv-Welch (LZW)** compression and decompression system. The core contribution is the implementation of the dictionary using three different data structures to analyze performance trade-offs:

1.  **Task 1:** Baseline LZW using a **Simple Array** (Linear Search).

2.  **Task 2:** LZW using a **Trie** (Prefix Tree).

3.  **Task 3:** LZW using a **Patricia Trie** (Radix Tree) with edge splitting.

For each method, the system produces a compressed binary file and a CSV dump of the dictionary.

* * * * *

Files in Submission
-------------------

-   `lzw_array.py` - Task 1 implementation (Array-based dictionary).

-   `lzw_trie.py` - Task 2 implementation (Trie-based dictionary).

-   `lzw_patricia.py` - Task 3 implementation (Patricia Trie-based dictionary).

-   `generate_test_files.py` - Script to generate the test datasets (English, Genome, Source, Synthetic).

-   `Report.pdf` - Detailed project report and experimental analysis.

* * * * *

How to Run the Project
----------------------

### 1\. Prerequisites

-   **Python 3.x** is required.

-   No external libraries are needed (uses standard `sys`, `struct`, `time`, `os`, `csv`, `random`).

### 2\. Generate Test Data

Before running the compressors, generate the required test files (Genome, Synthetic, Source Code) by running:

Bash

```
python generate_test_files.py

```

This will create:

-   `test_genome.txt` (1 MB)

-   `test_synthetic.txt` (1 MB)

-   `test_source.txt` (~8 KB)

-   (Ensure you also have `english.txt` in the folder)

### 3\. Running the Compressors

You can run each script independently. By default, they are configured to compress `english.txt` (or you can edit the `test_input` variable in the `__main__` block of each script to test other files).

**Task 1: Array (Baseline)**

Bash

```
python lzw_array.py

```

-   **Output:** `test_output.lzw`, `test_restored.txt`, `dict_compressor.csv`

**Task 2: Trie**

Bash

```
python lzw_trie.py

```

-   **Output:** `test_output_trie.lzw`, `test_restored_trie.txt`, `dict_trie_compressor.csv`

**Task 3: Patricia Trie**

Bash

```
python lzw_patricia.py

```

-   **Output:** `test_output_patricia.lzw`, `test_restored_patricia.txt`, `dict_patricia_compressor.csv`

### 4\. Changing Input Files

To test different files (e.g., Genome or Synthetic data), open any of the python scripts in a text editor and modify the `test_input` line at the bottom:

Python

```
if __name__ == "__main__":
    # Change this filename to test different inputs
    test_input = "test_genome.txt"
    ...

```

* * * * *

Output Verification
-------------------

Each script performs an automatic self-check after decompression:

1.  Compresses the input file.

2.  Decompresses the `.lzw` file back to text.

3.  Compares the restored file byte-by-byte with the original.

4.  **Success Message:** `SUCCESS: Decompressed file matches original exactly!`

* * * * *

Dictionary CSV Format
---------------------

As requested, the dictionary is dumped to a CSV file for inspection.

-   **Column 1:** Integer Code (e.g., `256`)

-   **Column 2:** String Representation (e.g., `'The'`)

* * * * *

Performance Summary
-------------------

Detailed analysis is provided in `Report.pdf`.

-   **Fastest:** Trie (Task 2)

-   **Most Memory Efficient:** Patricia Trie (Task 3) - Theoretical

-   **Slowest:** Array (Task 1) - Due to $O(N)$ linear search complexity.
