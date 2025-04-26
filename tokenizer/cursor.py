class Cursor:
    def __init__(self, position):
        # Position of the cursor in the whole text
        self.position = position
        # Binary (2 categories => 0 or 1) features of the cursor
        self.leftCharBinaryFeatures = {"isLeftWhitespace": 0,
                                       "isLeftUpperAlphabetical": 0,
                                       "isLeftLowerAlphabetical": 0,
                                       "isLeftNumber": 0,
                                       "isLeftPeriod": 0,
                                       "isLeftApostrophe": 0,
                                       "isLeftOtherEOS": 0,
                                       "isLeftOther": 0}
        self.rightCharBinaryFeatures = {"isRightWhitespace": 0,
                                        "isRightUpperAlphabetical": 0,
                                        "isRightLowerAlphabetical": 0,
                                        "isRightNumber": 0,
                                        "isRightPeriod": 0,
                                        "isRightApostrophe": 0,
                                        "isRightOtherEOS": 0,
                                        "isRightOther": 0}
        # Numerical features of the cursor (limit each feature to a maximum value of 100)
        self.numericalFeatures = {"distanceToLeftWhitespace": 100,
                                  "distanceToLeftUpperAlphabetical": 100,
                                  "distanceToLeftLowerAlphabetical": 100,
                                  "distanceToLeftNumber": 100,
                                  "distanceToLeftPeriod": 100,
                                  "distanceToLeftApostrophe": 100,
                                  "distanceToLeftOtherEOS": 100,
                                  "distanceToLeftOther": 100}
        # # Bigram features of the cursor (complex features in the form of strings which require
        # # preprocessing/conversion to numbers before being fed to the model)
        # self.bigramFeatures = {"bigramLeft": "",
        #                        "bigramRight": ""}
        # Ground truth label of the cursor (if the cursor position is the start of a new token or not)
        self.label = 0
