import os
import re


def split_corpus(input_corpus_path, output_dir, output_files_prefix, file_size):
    """
    Split a large text file into smaller chunks, ensuring that chunks end with the end of a sentence.

    :param input_file: Path to the large input text file.
    :param output_dir: Directory where the output chunks will be stored.
    :param max_chunk_size: Maximum size of each chunk in bytes (e.g., 100 MB = 100 * 1024 * 1024).
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Try to split corpora from the sentence boundaries (try not to divide a sentence into 2 different
    # files). It's not a perfect sentence splitter at this point, but based on observation of the corpora,
    # a period between whitespaces, and followed by an uppercase letter is selected.
    sentence_boundary_regex = re.compile(r'\s\.\s[A-Z]')

    # Open the large input file in read mode
    with open(input_corpus_path, 'r', encoding='utf-8') as corpus:
        file_index = 1
        file_buffer = ""
        check_buffer = None

        file_buffer = corpus.read(file_size)
        print("-----------FILE BUFFER----------\n", file_buffer)

        check_buffer = corpus.read(500)
        print("-----------CHECK BUFFER----------\n", check_buffer)

        match = sentence_boundary_regex.search(check_buffer)
        print(match)
        print(match.lastindex)
        print(match.group())
        print(match.groups())
        print(match.start())
        print(match.end())
        print(check_buffer[:match.end()-2])
        print(check_buffer[match.end()-2:])

        # while True:
        #     # Read the next chunk of the file
        #     chunk = f.read(max_chunk_size)
        #
        #     if not chunk:
        #         # If no more content to read, write the remaining buffer and break
        #         if buffer:
        #             output_file = os.path.join(output_dir, f"chunk_{chunk_index}.txt")
        #             with open(output_file, 'w', encoding='utf-8') as chunk_file:
        #                 chunk_file.write(buffer)
        #             print(f"Created: {output_file}")
        #         break
        #
        #     buffer += chunk
        #
        #     # Read ahead to find the next sentence boundary after the chunk
        #     extra_chunk = f.read(1024 * 1024)  # Read an additional 1MB to find the next sentence boundary
        #     match = sentence_boundary_regex.search(extra_chunk)
        #
        #     if match:
        #         # If we find a match in the extra_chunk, split at that point
        #         split_point = match.end() - 1  # -1 to stop at the period
        #         chunk_to_write = buffer + extra_chunk[:split_point + 1]  # Include up to the period
        #         buffer = extra_chunk[split_point + 1:]  # Save the rest of the extra_chunk for the next round
        #
        #         # Write the current chunk
        #         output_file = os.path.join(output_dir, f"chunk_{chunk_index}.txt")
        #         with open(output_file, 'w', encoding='utf-8') as chunk_file:
        #             chunk_file.write(chunk_to_write)
        #
        #         print(f"Created: {output_file}")
        #
        #         # Increment chunk index
        #         chunk_index += 1
        #     else:
        #         # If no sentence boundary found, append extra_chunk to the buffer
        #         buffer += extra_chunk


# Path to the large corpora to split
input_corpus_path = "../corpora/TS-Corpus/split-draft/draft_corpus.txt"
# Output directory path for the split files
output_dir = "../corpora/TS-Corpus/split-draft"
# Common prefix for the split files (each file name starts with this string)
output_files_prefix = "draft"
# Size of the split files in bytes (selected as 1000 bytes)
file_size = 1000

split_corpus(input_corpus_path, output_dir, output_files_prefix, file_size)