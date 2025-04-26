import pickle

def add_mwe_to_dict(mwe_dict, mwe):
    """
    Add an MWE to the MWE dictionary (in the form of a nested hash table).

    Args:
        mwe_dict (dict): The nested hash table to store MWEs.
        mwe (list): List of words in the MWE.
    """

    current_level = mwe_dict

    # For the words in mwe
    for i, word in enumerate(mwe):

        # If this word is seen for the first time in the current level
        if word not in current_level.keys():
            # Add the word to the level, and set the value to a new empty dict (a new level
            # for potential next words)
            current_level[word] = {}

        # Move to the next dict in the nested structure (representing possible next words
        # in the mwe)
        current_level = current_level[word]

        # If this was the last word of the mwe
        if i == len(mwe) - 1:
            # Add a special element to mark the end of the mwe
            current_level["END"] = True


def extract_MWEs_into_dict(file_path, mwe_dict):
    """
    Parse a .cupt file, extract MWEs from sentences and add them to the MWE dictionary.

    Args:
        file_path (string): Path to the .cupt file.
        mwe_dict (dict): The nested hash table that stores MWEs.
    """

    # Dictionary to store the MWEs in the currently parsed sentence
    sentence_MWEs = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        # Check each line in the file
        for line in file:

            # If line is an empty line or starts with a '#' character, then it either marks the
            # end of the sentence, or is an id/info line.
            if line.strip() == "" or line.startswith("#"):
                # In that case, add the MWEs (if present) in the current sentence to the dictionary
                if len(sentence_MWEs) > 0:
                    for mwe in sentence_MWEs.values():
                        # print(mwe)
                        add_mwe_to_dict(mwe_dict, mwe)

                # And reset sentence
                current_mwe = sentence_MWEs.clear()

            # If it is a word line
            else:
                # Split word line into columns
                columns = line.strip().split("\t")
                # .cupt format should have 11 columns (10 columns from .connlu format + 1 additional
                # column for mwe info). If otherwise, assume invalid line and continue.
                if len(columns) < 11:
                    continue

                # Get last column which holds mwe info
                mwe_info = columns[10]
                # Also get the pos tag of the word (because we will ignore "aux" and "punct" types that belong
                # to MWEs as they're not complete words, they won't be added to dictionary)
                pos_tag = columns[3].lower()

                # If word is not part of a mwe, or undefined, or ignored type, continue
                if mwe_info == "*" or mwe_info == "_" or (pos_tag in ["aux", "punct"]):
                    continue
                # If word is a valid part of a mwe
                else:
                    # It is possible that one word may be part of multiple MWEs, in that case
                    # the info is separated by a ";", so we split by it to get info of each part (each MWE)
                    mwe_parts = mwe_info.split(";")

                    for part in mwe_parts:
                        # Get the id of the mwe part, they can be of the form 1:VID, 2:LVC or just 1, 2 etc.
                        mwe_id = part.split(":")[0]

                        # If this id appears for the first time in the sentence, then it is the beginning of a new MWE
                        if mwe_id not in sentence_MWEs.keys():
                            # Then, add a new list to hold words of mwe with this id
                            sentence_MWEs[mwe_id] = []

                        # Append the lemma of this word as the next word in the mwe
                        lemma = columns[2].lower()
                        sentence_MWEs[mwe_id].append(lemma)


# Initialize empty mwe dictionary
mwe_dict = {}

# Files used to build mwe dictionary
train_path = "../corpora/PARSEME corpora annotated for verbal multiword expressions (version 1.3)/TR/train.cupt"
test_path = "../corpora/PARSEME corpora annotated for verbal multiword expressions (version 1.3)/TR/test.cupt"
dev_path = "../corpora/PARSEME corpora annotated for verbal multiword expressions (version 1.3)/TR/dev.cupt"
file_paths = [train_path, test_path, dev_path]

print("Building MWE dictionary using files:")
for file_path in file_paths:
    print("\t" + file_path)
print()

# Build dictionary from files
for file_path in file_paths:
    extract_MWEs_into_dict(file_path, mwe_dict)

# Export the dictionary to a file using pickle
export_file_path = "./mwe_dict.pkl"
with open(export_file_path, "wb") as file:
    pickle.dump(mwe_dict, file)
    print(f"Build completed, dictionary exported to file:\n\t{export_file_path}")
