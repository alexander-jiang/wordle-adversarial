"""
given state of the clues, return a list of possible answer words
& a list of possible guesses (useful for playing vanilla Wordle)

and thus also useful for adversarial Wordle
"""
from abc import ABC, abstractmethod
from typing import List
from wordle.wordle_clues import WordleClues


class WordListSearcherABC(ABC):
    @abstractmethod
    def load_words(self, word_list: List[str]) -> int:
        """
        Adds the words to the list and returns the number of words that were added
        (excludes duplicates).
        """
        pass

    @abstractmethod
    def match(self, clues: WordleClues) -> List[str]:
        """
        Returns all words (in the word list) that match the given clues.
        """
        pass


class WordListSearcher(WordListSearcherABC):
    def __init__(self):
        self.word_set = set()

    def load_words(self, word_list: List[str]) -> int:
        new_words = set(word_list)
        num_new_words = len(new_words - self.word_set)
        self.word_set |= new_words
        return num_new_words

    def match(self, clues: WordleClues) -> List[str]:
        return [candidate for candidate in self.word_set if clues.check(candidate)]