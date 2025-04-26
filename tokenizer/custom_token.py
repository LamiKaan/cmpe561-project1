from enum import Enum

class TokenType(Enum):
    WORD = 0
    MWE = 1
    EMAIL = 2
    URL = 3
    DATE = 4
    TIME = 5
    NUMBER = 6
    HASHTAG = 7
    END_OF_SENTENCE_PUNCTUATION = 8
    OTHER = 9

class Token:
    def __init__(self, id, text, token_type):
        self.id = id
        self.text = text
        self.token_type = token_type

    def __repr__(self):
        return f"Token(id={self.id}, text='{self.text}', token_type={self.token_type})"

    def __str__(self):
        return f"{self.text}"
