import unittest, logging

from utils.trivia import TriviaData

class TestTriviaGuess(unittest.TestCase):
    triva = TriviaData()

    def test_exact(self):
        self.assertEqual(trivia.check_guess('hello', 'hello'), True)