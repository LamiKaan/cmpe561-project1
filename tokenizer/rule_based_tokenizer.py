import pickle
import re
from enum import Enum
from .custom_token import *

class InputType(Enum):
    FILE_PATH = 0
    STRING = 1
    LIST = 2

class Patterns(Enum):
    WHITESPACE = re.compile(r'\s+')
    EMAIL = re.compile(r'[a-zA-Z0-9]+([\._-]?[a-zA-Z0-9]+)*@([a-zA-Z]+\.)+[a-zA-Z]{2,}\b')
    URL = re.compile(r'(https?://)?(www\.)?([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}(/[a-zA-Z0-9=&%+-_\?\.]*)*\b')
    DATE = re.compile(r'(0?[1-9]|[12][0-9]|3[01])([\.-/])(0?[1-9]|1[0-2])\2(\d{4})(\'[ûâçğıöşüa-z]+)?\b')
    TIME = re.compile(r'([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?(\'[ûâçğıöşüa-z]+)?\b')
    NUMBER = re.compile(r'\d{1,3}(([.,]\d{3})*|\d+)*([.,]\d+)?(\'[ûâçğıöşüa-z]+)?\b')
    HASHTAG = re.compile(r'#[ûâçğıöşüÇĞİÖŞÜa-zA-Z0-9_]+\b')
    # WORD = re.compile(r'[ûâçğıöşüÇĞİÖŞÜa-zA-Z]+((\'[ûâçğıöşüa-z]+)?|(-[ûâçğıöşüÇĞİÖŞÜa-zA-Z]+)*)\b')
    WORD = re.compile(r'[ûâçğıöşüÇĞİÖŞÜa-zA-Z]+(-[ûâçğıöşüÇĞİÖŞÜa-zA-Z]+)*(\'[ûâçğıöşüa-z]+)?\b')
    END_OF_SENTENCE_PUNCTUATION = re.compile(r'\.\.\.|[\.\!\?…]')
    ONLY_LETTER_SEQUENCE = re.compile(r'[ûâçğıöşüÇĞİÖŞÜa-zA-Z]{2,}\b')


def check_MWE(text, mwe_dict):
    """
    Check if the start of a text matches a MWE.

    Args:
        text (string): Text to be searched for MWE.
        mwe_dict (dict): The nested hash table that stores MWEs.

    Returns:
        is_MWE (bool): True if the text matches a MWE, False otherwise.
        text_MWE (string): Part of text that matches the MWE.
    """
    traversed = ""
    current_levels = [mwe_dict]

    while True:
        # Detect whitespaces from the head of the text, and traverse that part of the text
        whitespace_match = Patterns.WHITESPACE.value.match(text[len(traversed):])
        if whitespace_match is not None:
            traversed += whitespace_match.group()

        # MWEs can only consist of multiple words (alphabetical characters only)
        # Match an alphabetical sequence (of length 2 or more for a valid Turkish word) from text
        match = Patterns.ONLY_LETTER_SEQUENCE.value.match(text[len(traversed):])

        # If no such match is found
        if match is None:

            # If match is absent before any text has been traversed, then there is no MWE
            if len(traversed) == 0:
                return (False, None)

            # If match is absent after some text has been traversed
            else:

                # Check current levels to see if any of them yields to a valid MWE
                for level in current_levels:
                    # If we've reached the end of a valid MWE
                    if ("END" in level) and (level["END"] == True):
                        # Then, there is a MWE, traversed text is the MWE text
                        return (True, traversed)

                # If no level yielded to the end of a valid MWE, there is no MWE
                return (False, None)

        # If a match for a letter only word is found
        else:
            # Create a new empty list to hold the potential new levels
            new_levels = []
            # Get text of the match object and convert to lowercase
            match_lower = match.group().lower()

            # Check the keys of every relevant level of the MWE dictionary
            for level in current_levels:
                for key in level.keys():
                    # If the matched text starts with a key from the current level, it contains
                    # a word that is an element of a MWE (Also check if it starts with the key except
                    # key's last letter. As keys, words of a MWE, are kept in their lemma form, the last
                    # letter may get inflected as a result of attached suffix in the text)
                    # if match_lower.startswith(key) or match_lower.startswith(key[:-1]):
                    # Changed it to exact match as it created too many incorrect MWE tokens
                    if match_lower.startswith(key):
                        # Append the value of this key to the new_levels
                        new_levels.append(level[key])

            # If the match text didn't produce any new levels
            if len(new_levels) == 0:
                # Check current levels to see if any of them yields to a valid MWE
                for level in current_levels:
                    # If we've reached the end of a valid MWE
                    if ("END" in level) and (level["END"] == True):
                        # Then, there is a MWE, traversed text is the MWE text
                        return (True, traversed)

                # If no level yielded to the end of a valid MWE, there is no MWE
                return (False, None)

            # If match text produced new levels
            else:
                # Traverse the match text
                traversed += match.group()

                # Update current levels
                current_levels = new_levels

                # And continue checking the rest of the text
                continue


def tokenize_text(text, mwe_dict):
    """
    Separate a given text into tokens by continuously checking if a specific
    token type occurs (matches) at the current cursor position.

    Args:
        text (string): Text to be tokenized.
        mwe_dict (dict): The nested hash table that stores MWEs.

    Returns:
        tokens (list): A list of tokens (kept as custom_token objects)
    """
    tokens = []
    next_token_id = 0
    cursor = 0
    text_length = len(text)

    while cursor < text_length:
        # Remove leading whitespaces
        whitespace_match = Patterns.WHITESPACE.value.match(text[cursor:])
        if whitespace_match is not None:
            cursor += len(whitespace_match.group())

        if cursor >= text_length:
            break

        # Check for MWE match
        is_MWE, text_MWE = check_MWE(text[cursor:], mwe_dict)
        if is_MWE:
            cursor += len(text_MWE)
            tokens.append(Token(next_token_id, text_MWE.strip(), TokenType.MWE))
            next_token_id += 1
            continue

        # Check for email match
        email_match = Patterns.EMAIL.value.match(text[cursor:])
        if email_match:
            cursor += len(email_match.group())
            tokens.append(Token(next_token_id, email_match.group(), TokenType.EMAIL))
            next_token_id += 1
            continue

        # Check for URL match
        url_match = Patterns.URL.value.match(text[cursor:])
        if url_match:
            cursor += len(url_match.group())
            tokens.append(Token(next_token_id, url_match.group(), TokenType.URL))
            next_token_id += 1
            continue

        # Check for date match
        date_match = Patterns.DATE.value.match(text[cursor:])
        if date_match:
            cursor += len(date_match.group())
            tokens.append(Token(next_token_id, date_match.group(), TokenType.DATE))
            next_token_id += 1
            continue

        # Check for time match
        time_match = Patterns.TIME.value.match(text[cursor:])
        if time_match:
            cursor += len(time_match.group())
            tokens.append(Token(next_token_id, time_match.group(), TokenType.TIME))
            next_token_id += 1
            continue

        # Check for number match
        number_match = Patterns.NUMBER.value.match(text[cursor:])
        if number_match:
            cursor += len(number_match.group())
            tokens.append(Token(next_token_id, number_match.group(), TokenType.NUMBER))
            next_token_id += 1
            continue

        # Check for hashtag match
        hashtag_match = Patterns.HASHTAG.value.match(text[cursor:])
        if hashtag_match:
            cursor += len(hashtag_match.group())
            tokens.append(Token(next_token_id, hashtag_match.group(), TokenType.HASHTAG))
            next_token_id += 1
            continue

        # Check for word match
        word_match = Patterns.WORD.value.match(text[cursor:])
        if word_match:
            cursor += len(word_match.group())
            tokens.append(Token(next_token_id, word_match.group(), TokenType.WORD))
            next_token_id += 1
            continue

        # Check for end of sentence puncuation match
        eos_punc_match = Patterns.END_OF_SENTENCE_PUNCTUATION.value.match(text[cursor:])
        if eos_punc_match:
            cursor += len(eos_punc_match.group())
            tokens.append(Token(next_token_id, eos_punc_match.group(), TokenType.END_OF_SENTENCE_PUNCTUATION))
            next_token_id += 1
            continue

        # If none of the previous patterns matched, just take one character and
        # save it as a token of type "OTHER" (probably any other type of punctuation/special character)
        other_match = text[cursor]
        if len(other_match) > 0:
            cursor += len(other_match)
            tokens.append(Token(next_token_id, other_match, TokenType.OTHER))
            next_token_id += 1
            continue

    return tokens


def main(input, input_type):
    """
    Main function to test the rule based tokenizer. Takes an input and prints
    the tokens to the screen.

    Args:
        input (string): A file path (file whose text we want to tokenize), or a plain text (string to be tokenized)
        input_type (InputType): InputType.FILE_PATH or InputType.STRING (based on the type of the provided input)
    """
    # Load the MWE dictionary from the pickle file
    mwe_dict_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/mwe_dict.pkl"
    with open(mwe_dict_path, "rb") as file:
        mwe_dict = pickle.load(file)

    # Get the text to tokenize (either from a file path or directly as input)
    if input_type == InputType.FILE_PATH:
        # Retrieve the text to tokenize from the file path
        with open(input, "r", encoding="utf-8") as file:
            text_to_tokenize = file.read()
    else:
        text_to_tokenize = input

    # Tokenize text
    tokens = tokenize_text(text_to_tokenize, mwe_dict)

    for token in tokens:
        print(token)


def main2(input, input_type):
    """
    eturn token list instead of printing each token.
    """
    # Load the MWE dictionary from the pickle file
    mwe_dict_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/mwe_dict.pkl"
    with open(mwe_dict_path, "rb") as file:
        mwe_dict = pickle.load(file)

    # Get the text to tokenize (either from a file path or directly as input)
    if input_type == InputType.FILE_PATH:
        # Retrieve the text to tokenize from the file path
        with open(input, "r", encoding="utf-8") as file:
            text_to_tokenize = file.read()
    else:
        text_to_tokenize = input

    # Tokenize text
    tokens = tokenize_text(text_to_tokenize, mwe_dict)

    return tokens
