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
from sklearn import metrics
from joblib import dump, load
from .train_ml_tokenizer import Patterns, analyzeEachCursorPosition
from .rule_based_tokenizer import InputType


def createFeatureMatrix(text):
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

        cursors.append(cursor)

    # Create lists of dictionaries (feature lists) to create corresponding dataframes
    indices = []
    leftCharFeatures = []
    rightCharFeatures = []
    numericalFeatures = []

    # For each cursor position, populate dictionary lists with corresponding features
    for cursor in cursors:
        indices.append(cursor.position)
        leftCharFeatures.append(cursor.leftCharBinaryFeatures)
        rightCharFeatures.append(cursor.rightCharBinaryFeatures)
        numericalFeatures.append(cursor.numericalFeatures)

    # Create the dataframes
    dfLeft = pd.DataFrame(leftCharFeatures, index=indices)
    dfRight = pd.DataFrame(rightCharFeatures, index=indices)
    dfNum = pd.DataFrame(numericalFeatures, index=indices)

    # Scale the dfNum dataframe (as it contains numerical features)
    scaler = MinMaxScaler()
    scaledValues = scaler.fit_transform(dfNum)
    dfNumScaled = pd.DataFrame(scaledValues, columns=dfNum.columns)

    # Concatenate all feature dataframes
    dfAllFeatures = pd.concat([dfLeft, dfRight, dfNumScaled], axis=1)

    # Create numpy arrays for test feature matrice
    X_test = np.array(dfAllFeatures)

    return X_test


def createTokenList(text, y):
    # List to store tokens
    tokens = []

    # Variable to keep the index of last token boundary (first character is always a token boundary)
    lastPositiveIndex = 0

    for i in range(1, len(y)):

        if i < len(text):
            if y[i] == 1:
                tokens.append(text[lastPositiveIndex:i].strip())
                lastPositiveIndex = i
            else:
                continue
        else:
            tokens.append(text[lastPositiveIndex:].strip())
            break

    return tokens


def createLabelMatrix(text, tokens):
    # Build a linked list from the token list
    tokenLinkedList = deque(tokens)

    # Helper function to get the next token from the linked list
    def getNextToken():
        return tokenLinkedList.popleft() if len(tokenLinkedList) > 0 else None

    # Next token in the text
    nextToken = getNextToken()
    # List to store all cursor objects
    cursors = []

    # For each cursor position in the text (if text is of size N, it has N+1 cursor positions)
    for i in range(len(text) + 1):
        # Create cursor object
        cursor = Cursor(i)

        # Check for the label (if current cursor position is the start of a new token or not)
        if nextToken is not None:
            if text[i: i + len(nextToken)] == nextToken:
                cursor.label = 1
                nextToken = getNextToken()
        else:
            if i == len(text):
                cursor.label = 1

        cursors.append(cursor)

    # Create lists for indices and labels
    indices = []
    labels = []

    # Populate the lists with info from each cursor position
    for cursor in cursors:
        indices.append(cursor.position)
        labels.append(cursor.label)

    # Create the label dataframe and label matrix
    dfLabels = pd.DataFrame(labels, index=indices)
    y = np.array(dfLabels).ravel()

    return y


def computeModelPerformance(text, y_test, ground_truth_path):
    # Load the ground truth token list corresponding to the test text file
    with open(ground_truth_path, "rb") as file:
        tokens_gt = pickle.load(file)

    # Create label matrix from ground truth token list
    y_test_gt = createLabelMatrix(text, tokens_gt)

    # Calculate performance metrics
    accuracy = metrics.accuracy_score(y_test, y_test_gt)
    recall = metrics.recall_score(y_test, y_test_gt)
    precision = metrics.precision_score(y_test, y_test_gt)
    f1 = metrics.f1_score(y_test, y_test_gt)

    dfMetrics = pd.DataFrame({'Accuracy': accuracy, 'Recall': recall, 'Precision': precision, 'F1': f1},
                             index=['Score'])

    return dfMetrics



def main(input, input_type, ground_truth_path=None):
    """
    Main function to test the ml based tokenizer. Takes an input and prints
    the tokens to the screen. Optionally calculates and prints model performance metrics.

    Args:
        input (string): A file path (file whose text we want to tokenize), or a plain text (string to be tokenized)
        input_type (InputType): InputType.FILE_PATH or InputType.STRING (based on the type of the provided input)
        ground_truth_path (string): Path of the (serialized, pickle) file holding the list of ground truth tokens for the provided input.
    """

    # Get the text to tokenize (either from a file path or directly as input)
    if input_type == InputType.FILE_PATH:
        # Retrieve the text from the file path
        with open(input, "r", encoding="utf-8") as file:
            text = file.read()
    else:
        text = input

    # Create the feature matrix for the text to be tokenized
    X_test = createFeatureMatrix(text)

    # Load the trained ml tokenizer
    model_file_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/ml_model.joblib"
    model = load(model_file_path)

    # Make predictions
    y_test = model.predict(X_test)

    # Create the token list from the predictions
    tokens = createTokenList(text, y_test)

    # Print tokens
    for token in tokens:
        print(token)

    # OPTIONALLY COMPUTE PERFORMANCE METRICS FOR THE ML MODEL
    if ground_truth_path is not None:
        metrics = computeModelPerformance(text, y_test, ground_truth_path)
        print("\nModel Performance:")
        print(metrics)


def main2(input, input_type):
    """
    Does same thing as main function but returns the list of tokens instead of printing them.
    """

    # Get the text to tokenize (either from a file path or directly as input)
    if input_type == InputType.FILE_PATH:
        # Retrieve the text from the file path
        with open(input, "r", encoding="utf-8") as file:
            text = file.read()
    else:
        text = input

    # Create the feature matrix for the text to be tokenized
    X_test = createFeatureMatrix(text)

    # Load the trained ml tokenizer
    model_file_path = "/Users/lkk/Documents/BOUN CMPE/CMPE 561-Natural Language Processing/Application Project 1/tokenizer/ml_model.joblib"
    model = load(model_file_path)

    # Make predictions
    y_test = model.predict(X_test)

    # Create the token list from the predictions
    tokens = createTokenList(text, y_test)

    return tokens