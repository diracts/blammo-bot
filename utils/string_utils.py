import random


class AttemptedToScrambleWordWithLessThanTwoChars(Exception):
    pass


class ScrambleAttemptsExceededException(Exception):
    pass


def safe_scramble_word(word: str) -> str:
    """
    Provides a safe way to scramble a word.

    - Prevents from scrambling words with less than 2 characters.
    - Puts a maximum cap on the number of attempts to scramble the word
      to prevent infinite loops from emotes like `AAAA`.
    """

    MAX_ATTEMPTS = 500

    if len(word) < 2:
        raise AttemptedToScrambleWordWithLessThanTwoChars

    chars = list(word)

    for _ in range(MAX_ATTEMPTS):
        random.shuffle(chars)
        scrambled_word = "".join(chars)
        if scrambled_word.lower() != word.lower():
            return scrambled_word

    raise ScrambleAttemptsExceededException
