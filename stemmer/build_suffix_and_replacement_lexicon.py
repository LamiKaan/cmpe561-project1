from collections import Counter
import pickle


def compile_replacement_dict(replacement_dict):
    def find_most_frequent_string_in_list(list):
        counts = Counter(list)
        max_count = max(counts.values())
        # Retrieve the first string with the maximum count
        for string in list:
            if counts[string] == max_count:
                return string

    for key in replacement_dict.keys():
        most_frequent_replacement = find_most_frequent_string_in_list(replacement_dict[key])
        replacement_dict[key] = most_frequent_replacement


def add_replacement_to_dict(replacement_dict, replacement, suffix):
    """
    Add a replacement for a particular suffix to the replacement dictionary.

    Args:
        replacement_dict (dict): Dictionary to store suffixes and corresponding replacements.
        replacement (string): The replacement to replace the suffix with.
        suffix (string): Suffix string.
    """

    if suffix not in replacement_dict.keys():
        replacement_dict[suffix] = []
        replacement_dict[suffix].append(replacement)
    else:
        replacement_dict[suffix].append(replacement)


def add_suffix_to_dict(suffix_dict, suffix):
    """
    Add a suffix to the suffix dictionary (in the form of a nested hash table).

    Args:
        suffix_dict (dict): The nested hash table to store suffixes.
        suffix (string): Suffix string.
    """

    current_level = suffix_dict

    # For the characters in the suffix, from end to beginning
    for i, char in enumerate(reversed(suffix)):
        # If this char is seen for the first time in the current level
        if char not in current_level.keys():
            # Add the char to the level, and set the value to a new empty dict (a new level
            # for potential next (previous in unreversed order) chars of suffix)
            current_level[char] = {}

        # Move to the next dict in the nested structure (representing possible next chars
        # in the suffix)
        current_level = current_level[char]

        # If this was the last char of the suffix
        if i == len(suffix) - 1:
            # Add a special element to mark the end of the suffix
            current_level["END"] = True


def build_suffix_and_replacement_lexicon(file_path, suffix_dict, replacement_dict):
    """
    Parse a .connlu file, extract suffixes and required replacements from tokens and add them to the dicts.

    Args:
        file_path (string): Path to the .connlu file.
        suffix_dict (dict): The nested hash table that stores suffixes.
        replacement_dict (dict): The nested hash table that stores replacements.
    """

    # Helper function to add suffixes and replacements to the corresponding dicts using surface
    # and lemma form of the token
    def add_to_dicts(surfaceForm, lemmaForm):
        surfaceForm = surfaceForm.lower()
        lemmaForm = lemmaForm.lower()

        suffix = ""
        replacement = ""

        if lemmaForm.startswith(surfaceForm):
            return

        # if (len(surfaceForm) < len(lemmaForm)):
        #     print(surfaceForm, lemmaForm)

        for i in range(len(lemmaForm) + 1):

            if i < len(lemmaForm):
                if lemmaForm[i] == surfaceForm[i]:
                    continue
                else:
                    suffix = surfaceForm[i:]
                    replacement = lemmaForm[i:]
                    break
                # if i < len(lemmaForm):
                #     try:
                #         if lemmaForm[i] == surfaceForm[i]:
                #             continue
                #         else:
                #             suffix = surfaceForm[i:]
                #             replacement = lemmaForm[i:]
                #             break
                #     except IndexError as e:
                #         print("Index error occured")
                #         print(surfaceForm, lemmaForm)
                #         raise e
            else:
                suffix = surfaceForm[i:]
                replacement = ""
                break

        add_suffix_to_dict(suffix_dict, suffix)
        if replacement != "":
            add_replacement_to_dict(replacement_dict, replacement, suffix)


    # Variables to help keeping track of the tokens that span multiple lines in the .connlu file format
    multiIDToken = False
    startID = 0
    endID = 0
    surfaceToken = ""
    builtToken = ""
    lemmaToken = ""

    with open(file_path, 'r', encoding='utf-8') as file:
        # Check each line in the file
        for line in file:

            # If line is an empty line or starts with a '#' character, then it either marks the
            # end of the sentence, or is an id/info line. In that case, move to the next line.
            if line.strip() == "" or line.startswith("#"):
                continue

            # If it is a token line
            else:
                # Split token line into columns
                columns = line.strip().split("\t")
                # .connlu format should have 10 columns. If otherwise, assume invalid line and continue.
                if len(columns) < 10:
                    continue

                # Get first column which holds id of token in sentence
                IDinfo = columns[0]
                # Some lines start with a single ID (e.g. 8), but some other lines start with a range of ID (e.g. 10-11)
                # which represent a multi-ID token (holding info in subsequent multiple lines). Get the ID numbers in the
                # ID info column into a list
                IDs = list(map(lambda x: int(x), IDinfo.split("-")))
                # Get second column which holds the token (surface form string) corresponding to the current line
                surfaceForm = columns[1]
                # If the surface form doesn't only constitute of alphabetical characters, skip it
                if surfaceForm.isalpha() == False:
                    continue

                # In we're not already parsing a multi ID token
                if multiIDToken == False:

                    # If current line is the start of a multiID (multiline) token
                    if len(IDs) > 1:
                        multiIDToken = True
                        startID = IDs[0]
                        endID = IDs[-1]
                        # Keep the surface form of the token
                        surfaceToken = surfaceForm

                        if len(IDs) > 2:
                            print(line)

                        continue

                    # If the current line is a single ID token
                    else:
                        # Get third column which holds the lemma form of the token
                        lemmaForm = columns[2]
                        # If the surface and lemma forms are different, then we have a suffix
                        if surfaceForm != lemmaForm:
                            add_to_dicts(surfaceForm, lemmaForm)
                            continue

                # If we're parsing a line of a multiID token
                else:
                    tokenID = IDs[0]

                    if (tokenID < startID) or (tokenID > endID):
                        print(startID, tokenID, endID)
                        print(line)
                        raise ValueError("Invalid token ID for multiline token")

                    if tokenID == startID:
                        startSurface = columns[1]
                        startLemma = columns[2]

                        lemmaToken = startLemma
                        builtToken = startSurface

                        continue

                    if tokenID == endID:
                        endSurface = columns[1]
                        endUpos = columns[2].lower()

                        builtToken += endSurface
                        if (builtToken != surfaceToken) or (endUpos not in ["aux", "part"]):
                            multiIDToken = False
                            startID = 0
                            endID = 0
                            surfaceToken = ""
                            builtToken = ""
                            lemmaToken = ""

                            continue

                        else:
                            add_to_dicts(surfaceToken, lemmaToken)

                            multiIDToken = False
                            startID = 0
                            endID = 0
                            surfaceToken = ""
                            builtToken = ""
                            lemmaToken = ""

                            continue


# Initialize empty dictionaries
suffix_dict = {}
replacement_dict = {}

# Files used to build dictionaries
boun_train = "../corpora/UD_Turkish-BOUN/tr_boun-ud-train.conllu"
boun_dev = "../corpora/UD_Turkish-BOUN/tr_boun-ud-dev.conllu"
# boun_test = "../corpora/UD_Turkish-BOUN/tr_boun-ud-test.conllu"
penn_train = "../corpora/UD_Turkish-Penn/tr_penn-ud-train.conllu"
penn_dev = "../corpora/UD_Turkish-Penn/tr_penn-ud-dev.conllu"
penn_test = "../corpora/UD_Turkish-Penn/tr_penn-ud-test.conllu"

# file_paths = [boun_train, boun_dev, boun_test, penn_train, penn_dev, penn_test]
file_paths = [boun_train, boun_dev, penn_train, penn_dev, penn_test]

print("Building MWE dictionary using files:")
for file_path in file_paths:
    print("\t" + file_path)
print()

# Build dictionaries from files
for file_path in file_paths:
    # print(file_path)
    build_suffix_and_replacement_lexicon(file_path, suffix_dict, replacement_dict)

# Compile replacement dictionary (handles duplicates)
compile_replacement_dict(replacement_dict)

# Export the dictionaries to files using pickle
suffix_export_path = "./suffix_dict.pkl"
with open(suffix_export_path, "wb") as file:
    pickle.dump(suffix_dict, file)
    print(f"Build completed, suffix dictionary exported to file:\n\t{suffix_export_path}")

replacement_export_path = "./replacement_dict.pkl"
with open(replacement_export_path, "wb") as file:
    pickle.dump(replacement_dict, file)
    print(f"Build completed, replacement dictionary exported to file:\n\t{replacement_export_path}")