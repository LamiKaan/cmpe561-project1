import pickle


def build_token_list(file_path):
    """
    Parse a .connlu file, extract tokens from sentences and add them to the token list.

    Args:
        file_path (string): Path to the .connlu file.

    Returns:
        tokens (list): The list that stores tokens.
    """

    # List to store all tokens in the .connlu file
    tokens = []

    # Variables to help keeping track of the tokens that span multiple lines in the .connlu file format
    multiIDToken = False
    startID = 0
    endID = 0

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

                # Get first column which holds the id info of token in sentence
                IDinfo = columns[0]
                # Some lines start with a single ID (e.g. 8), but some other lines start with a range of ID (e.g. 10-11)
                # which represent a multi-ID token (holding info in subsequent multiple lines). Get the ID numbers in the
                # ID info column into a list
                IDs = list(map(lambda x: int(x), IDinfo.split("-")))
                # Get second column which holds the token (string) corresponding to the current line
                token = columns[1]

                # If it's not already a line representing a part of a multi ID token.
                if multiIDToken == False:

                    # Append the token to the list
                    tokens.append(token)

                    # Check if the current line represents a multiID token
                    if len(IDs) > 1:
                        # Keep info for subsequent lines
                        multiIDToken = True
                        startID = IDs[0]
                        endID = IDs[-1]

                # If the line is part of a multiline token
                else:
                    tokenID = IDs[0]

                    if (tokenID < startID) or (tokenID > endID):
                        print(startID, tokenID, endID)
                        print(line)
                        raise ValueError("Invalid token ID for multiline token")

                    # Once the last line of the corresponding multiID token is reached, reset kept info
                    if (tokenID == endID):
                        multiIDToken = False
                        startID = 0
                        endID = 0

    return tokens

# File used to build token list
file_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/corpora/UD_Turkish-BOUN/tr_boun-ud-test.conllu"

print("Building token list from the file:")
print("\t" + file_path)
print()

# Build token list from file
tokens = build_token_list(file_path)

# Export the list to a file using pickle
export_file_path = "./token_list_boun_test.pkl"
with open(export_file_path, "wb") as file:
    pickle.dump(tokens, file)
    print(f"Build completed, token list exported to file:\n\t{export_file_path}")

