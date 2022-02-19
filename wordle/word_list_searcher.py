"""
given state of the clues, return a list of possible answer words
& a list of possible guesses (useful for playing vanilla Wordle)

and thus also useful for adversarial Wordle
"""
from abc import ABC, abstractmethod
from typing import List
from wordle.constants import WORDLE_COLUMNS
from wordle.wordle_clues import WordleClues


def _is_valid_guess(user_input: str) -> bool:
    """ validate the string has the right length and uses valid chars [a-zA-Z] """
    return len(user_input) == WORDLE_COLUMNS and user_input.isalpha()


def _is_valid_clues(user_input: str) -> bool:
    """ validate the string has the right length and uses valid chars [RrYyGg] """
    if len(user_input) != WORDLE_COLUMNS:
        return False
    for idx in range(len(user_input)):
        if user_input[idx].lower() not in ("r", "y", "g"):
            return False
    return True


def _read_words_from_file(wordlist_path: str) -> List[str]:
    wordlist = []
    with open(wordlist_path, "r") as wordlist_file:
        for word in wordlist_file.readlines():
            word_lower = word.lower().strip()
            if not _is_valid_guess(word_lower):
                print(f"Found an invalid word: {word_lower}")
            wordlist.append(word_lower)
    return wordlist


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