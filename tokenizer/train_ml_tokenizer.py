import pickle
from collections import deque
from enum import Enum
from .cursor import *
import re
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from joblib import dump, load

class Patterns(Enum):
    WHITESPACE = re.compile(r"\s")
    UPPER_ALPHABETICAL = re.compile(r"[ÇĞİÖŞÜA-Z]")
    LOWER_ALPHABETICAL = re.compile(r"[ûâçğıöşüa-z]")
    NUMBER = re.compile(r"\d")
    PERIOD = re.compile(r"\.")
    APOSTROPHE = re.compile(r"\'")
    OTHER_EOS = re.compile(r'[\!\?…]')


def analyzeEachCursorPosition(text, tokens):
    # Build a linked list from the token list
    tokenLinkedList = deque(tokens)

    # Helper function to get the next token from the linked list
    def getNextToken():
        return tokenLinkedList.popleft() if len(tokenLinkedList) > 0 else None

    # Next token in the text
    nextToken = getNextToken()
    # List to store all cursor objects
    cursors = []

    # Variables for calculating numerical (distance) features of the cursor
    lastWhitespacePosition = None
    lastUpperAlphabeticalPosition = None
    lastLowerAlphabeticalPosition = None
    lastNumberPosition = None
    lastPeriodPosition = None
    lastApostrophePosition = None
    lastOtherEOSPosition = None
    lastOtherPosition = None

    # For each cursor position in the text (if text is of size N, it has N+1 cursor positions)
    for i in range(len(text) + 1):
        # Create cursor object
        cursor = Cursor(i)

        # Check for numerical features (which are limited to a maximum distance of 100)
        cursor.numericalFeatures["distanceToLeftWhitespace"] = min(i - lastWhitespacePosition,
                                                                   100) if lastWhitespacePosition is not None else 100
        cursor.numericalFeatures["distanceToLeftUpperAlphabetical"] = min(i - lastUpperAlphabeticalPosition,
                                                                          100) if lastUpperAlphabeticalPosition is not None else 100
        cursor.numericalFeatures["distanceToLeftLowerAlphabetical"] = min(i - lastLowerAlphabeticalPosition,
                                                                          100) if lastLowerAlphabeticalPosition is not None else 100
        cursor.numericalFeatures["distanceToLeftNumber"] = min(i - lastNumberPosition,
                                                               100) if lastNumberPosition is not None else 100
        cursor.numericalFeatures["distanceToLeftPeriod"] = min(i - lastPeriodPosition,
                                                               100) if lastPeriodPosition is not None else 100
        cursor.numericalFeatures["distanceToLeftApostrophe"] = min(i - lastApostrophePosition,
                                                                   100) if lastApostrophePosition is not None else 100
        cursor.numericalFeatures["distanceToLeftOtherEOS"] = min(i - lastOtherEOSPosition,
                                                                 100) if lastOtherEOSPosition is not None else 100
        cursor.numericalFeatures["distanceToLeftOther"] = min(i - lastOtherPosition,
                                                              100) if lastOtherPosition is not None else 100

        # Check for binary features of the char to the left of the current cursor position
        if i < 1:
            cursor.leftCharBinaryFeatures["isLeftWhitespace"] = 1
        else:
            if Patterns.WHITESPACE.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftWhitespace"] = 1
            elif Patterns.UPPER_ALPHABETICAL.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftUpperAlphabetical"] = 1
            elif Patterns.LOWER_ALPHABETICAL.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftLowerAlphabetical"] = 1
            elif Patterns.NUMBER.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftNumber"] = 1
            elif Patterns.PERIOD.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftPeriod"] = 1
            elif Patterns.APOSTROPHE.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftApostrophe"] = 1
            elif Patterns.OTHER_EOS.value.match(text[i - 1]) is not None:
                cursor.leftCharBinaryFeatures["isLeftOtherEOS"] = 1
            else:
                cursor.leftCharBinaryFeatures["isLeftOther"] = 1

        # Check for binary features of the char to the right of the current cursor position
        if i > len(text) - 1:
            cursor.rightCharBinaryFeatures["isRightWhitespace"] = 1
        else:
            if Patterns.WHITESPACE.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightWhitespace"] = 1
                lastWhitespacePosition = i
            elif Patterns.UPPER_ALPHABETICAL.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightUpperAlphabetical"] = 1
                lastUpperAlphabeticalPosition = i
            elif Patterns.LOWER_ALPHABETICAL.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightLowerAlphabetical"] = 1
                lastLowerAlphabeticalPosition = i
            elif Patterns.NUMBER.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightNumber"] = 1
                lastNumberPosition = i
            elif Patterns.PERIOD.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightPeriod"] = 1
                lastPeriodPosition = i
            elif Patterns.APOSTROPHE.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightApostrophe"] = 1
                lastApostrophePosition = i
            elif Patterns.OTHER_EOS.value.match(text[i]) is not None:
                cursor.rightCharBinaryFeatures["isRightOtherEOS"] = 1
                lastOtherEOSPosition = i
            else:
                cursor.rightCharBinaryFeatures["isRightOther"] = 1
                lastOtherPosition = i

        # # Check for bigram features
        # if (i > 1) and (i < len(text) - 1):
        #     cursor.bigramFeatures["bigramLeft"] = text[i-2:i]
        #     cursor.bigramFeatures["bigramRight"] = text[i:i+2]
        # else:
        #     if i == 0:
        #         cursor.bigramFeatures["bigramLeft"] = ". "
        #         cursor.bigramFeatures["bigramRight"] = text[i:i+2]
        #     elif i == 1:
        #         cursor.bigramFeatures["bigramLeft"] = " " + text[i-1:i]
        #         cursor.bigramFeatures["bigramRight"] = text[i:i+2]
        #     elif i == len(text) - 1:
        #         cursor.bigramFeatures["bigramLeft"] = text[i-2:i]
        #         cursor.bigramFeatures["bigramRight"] = text[i:i+1] + " "
        #     elif i == len(text):
        #         cursor.bigramFeatures["bigramLeft"] = text[i-2:i]
        #         cursor.bigramFeatures["bigramRight"] = " ."

        # Check for the label (if current cursor position is the start of a new token or not)
        if nextToken is not None:
            if text[i: i + len(nextToken)] == nextToken:
                cursor.label = 1
                nextToken = getNextToken()
        else:
            if i == len(text):
                cursor.label = 1

        cursors.append(cursor)

    return cursors


# Load the train text file
train_text_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/corpora/UD_Turkish-BOUN/tr_boun-ud-train.txt"
with open(train_text_path, "r", encoding="utf-8") as file:
    text = file.read()

# Load the token list corresponding to the train text file
tokens_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/token_list_boun_train.pkl"
with open(tokens_path, "rb") as file:
    tokens = pickle.load(file)

cursors = analyzeEachCursorPosition(text, tokens)

# Create lists of dictionaries (feature lists) to create corresponding dataframes
indices = []
leftCharFeatures = []
rightCharFeatures = []
numericalFeatures = []
labels = []

# For each cursor position, populate dictionary lists with corresponding features
for cursor in cursors:
    indices.append(cursor.position)
    leftCharFeatures.append(cursor.leftCharBinaryFeatures)
    rightCharFeatures.append(cursor.rightCharBinaryFeatures)
    numericalFeatures.append(cursor.numericalFeatures)
    labels.append(cursor.label)

# Create the dataframes
dfLeft = pd.DataFrame(leftCharFeatures, index=indices)
dfRight = pd.DataFrame(rightCharFeatures, index=indices)
dfNum = pd.DataFrame(numericalFeatures, index=indices)
dfLabels = pd.DataFrame(labels, index=indices)

# Scale the dfNum dataframe (as it contains numerical features)
scaler = MinMaxScaler()
scaledValues = scaler.fit_transform(dfNum)
dfNumScaled = pd.DataFrame(scaledValues, columns=dfNum.columns)

# Concatenate all feature dataframes
dfAllFeatures = pd.concat([dfLeft, dfRight, dfNumScaled], axis=1)

# Create numpy arrays for training feature and label matrices
X_train = np.array(dfAllFeatures)
y_train = np.array(dfLabels).ravel()

# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Dump the trained model to later use it in another module
model_file_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/ml_model.joblib"
dump(model, model_file_path)