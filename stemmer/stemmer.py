from tokenizer.ml_based_tokenizer import main2
from tokenizer.rule_based_tokenizer import InputType
import pickle

def detect_suffix_and_replacement(token, suffix_dict, replacement_dict):
    """
    If exists, detect the suffix part and the corresponding replacement for a token.

    Args:
        token (string): Token to be stemmed
        suffix_dict (dict): The nested hash table that stores suffixes.
        replacement_dict (dict): The dictionary that stores replacements for suffixes.

    Returns:
        suffix (string): Suffix part of the token.
        replacement (string): Part that will replace the removed suffix in the token.
    """

    possibleSuffixes = []
    possibleReplacements = []

    traversed = ""

    current_level = suffix_dict

    for char in token[::-1]:
        if char in current_level.keys():
            traversed += char
            current_level = current_level[char]
            if ("END" in current_level) and (current_level["END"] == True):
                possibleSuffix = traversed[::-1]
                possibleSuffixes.append(traversed)
                possibleReplacements.append(
                    replacement_dict[possibleSuffix] if possibleSuffix in replacement_dict else None)
                continue
            else:
                continue
        else:
            break

    if len(possibleSuffixes) == 0:
        return None, None
    else:
        for i in range(len(possibleSuffixes) - 1, -1, -1):
            suffix = possibleSuffixes[i]
            replacement = possibleReplacements[i]

            if replacement is not None:
                possibleStem = token[:-len(suffix)] + replacement
                if len(possibleStem) > 1:
                    return suffix, replacement
                if len(possibleStem) == 1 and possibleStem == "o":
                    return suffix, replacement
                else:
                    continue
            # If replacement is None
            else:
                possibleStem = token[:-len(suffix)]
                if len(possibleStem) > 1:
                    return suffix, None
                if len(possibleStem) == 1 and possibleStem == "o":
                    return suffix, None
                else:
                    continue

    return None, None


def detect_suffix(token, suffix_dict):
    """
    If exists, detect the suffix part for a token.

    Args:
        token (string): Token to be stemmed
        suffix_dict (dict): The nested hash table that stores suffixes.

    Returns:
        suffix (string): Suffix part of the token.
    """

    possibleSuffixes = []

    traversed = ""

    current_level = suffix_dict

    for char in token[::-1]:
        if char in current_level.keys():
            traversed += char
            current_level = current_level[char]
            if ("END" in current_level) and (current_level["END"] == True):
                possibleSuffix = traversed[::-1]
                possibleSuffixes.append(possibleSuffix)
                continue
            else:
                continue
        else:
            break

    if len(possibleSuffixes) == 0:
        return None
    else:
        for i in range(len(possibleSuffixes) - 1, -1, -1):
            suffix = possibleSuffixes[i]

            possibleStem = token[:-len(suffix)]
            if len(possibleStem) > 1:
                return suffix
            if len(possibleStem) == 1 and possibleStem == "o":
                return suffix
            else:
                continue

    return None


def main(input, input_type):
    # If the input is a file path or a string
    if input_type != InputType.LIST:
        # First, tokenize the text in the file/string using the ml based tokenizer.
        if input_type == InputType.FILE_PATH:
            input_tokens = main2(input, InputType.FILE_PATH)
        else:
            input_tokens = main2(input, InputType.STRING)

    # If input is directly provided as a list of tokens, just use it
    else:
        input_tokens = input

    # Remove tokens with non-alphabetical characters and feed the resulting token list to the stemmer
    tokens = []
    for token in input_tokens:
        if token.isalpha():
            tokens.append(token)

    # Load the suffix and replacement dictionaries from the pickle files
    suffix_dict_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/stemmer/suffix_dict.pkl"
    replacement_dict_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/stemmer/replacement_dict.pkl"
    with open(suffix_dict_path, "rb") as file:
        suffix_dict = pickle.load(file)
    with open(replacement_dict_path, "rb") as file:
        replacement_dict = pickle.load(file)

    stems = []

    # Detect the suffix part of the token from the suffix dictionary and remove it
    for token in tokens:
        suffix = detect_suffix(token, suffix_dict)
        if suffix is not None:
            stems.append(token[:-len(suffix)])
        else:
            stems.append(token)

    for i in range(len(stems)):
        print(f"Surface:{tokens[i]}, Stem:{stems[i]}")
