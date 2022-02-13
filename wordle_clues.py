"""
Representation of the information gathered in a Wordle game
(i.e. which letters are colored gray, which are colored yellow 
or green, and the remaining letters with no information)
"""
from abc import ABC, abstractmethod
from enum import Enum
from constants import WORDLE_COLUMNS
from typing import MutableSet, Dict, List

class WordleLetterState(Enum):
    GRAY = -1
    NO_INFO = 0
    YELLOW = 1
    GREEN = 2


class WordleCluesABC(ABC):
    @abstractmethod
    def mark(self, letter: str, state: WordleLetterState, position: int) -> None:
        """
        Updates the current instance of the clues to include the letter
        marked with the specific state.
        """
        pass

    @abstractmethod
    def check(self, word: str) -> bool:
        """
        Returns true if the word is possible, given the current set of clues.
        """
        pass


class WordleClues(WordleCluesABC):
    def __init__(self):
        # set of letters that are marked gray (cannot be in the answer word)
        self.gray_letters: MutableSet[str] = set([])

        # for each letter marked yellow, maps to a set containing a set of positions
        # -> the letter must appear in the word, must not appear in any position in the set
        self.yellow_letters: Dict[str, MutableSet[int]] = {}

        # for each letter marked green, maps to a set containing a set of positions
        # -> the letter must appear in the word, and must appear in all positions in the set
        self.green_letters: Dict[str, MutableSet[int]] = {}

    # def _reset(self):
    #     """Resets all letters to the no info state."""
    #     for letter_ord in range(ord('A'), ord('Z') + 1):
    #         letter = chr(letter_ord)
    #         for pos in range(WORDLE_COLUMNS):
    #             self.mark(letter, WordleLetterState.NO_INFO, pos)

    def mark(self, letter: str, state: WordleLetterState, position: int) -> None:
        assert len(letter) == 1 and ord('A') <= ord(letter) <= ord('Z'), (
            f'WordleClues.mark() must be called with a string containing a single upper-case letter, was instead called with {letter}'
        )
        assert state in [WordleLetterState.NO_INFO, WordleLetterState.GRAY, WordleLetterState.YELLOW, WordleLetterState.GREEN], (
            f'WordleClues.mark() must be called with valid state, was instead called with {position}'
        )
        assert 0 <= position < WORDLE_COLUMNS, (
            f'WordleClues.mark() must be called with position between 0 and {WORDLE_COLUMNS - 1}, was instead called with {position}'
        )
        if state == WordleLetterState.NO_INFO:
            # Clear the data structures
            self.gray_letters.remove(letter)
            if letter in self.yellow_letters:
                del self.yellow_letters[letter]
            if letter in self.green_letters:
                del self.green_letters[letter]
        elif state == WordleLetterState.GRAY:
            self.gray_letters.add(letter)
        elif state == WordleLetterState.YELLOW:
            if letter not in self.yellow_letters:
                self.yellow_letters[letter] = set([])
            self.yellow_letters[letter].add(position)
        elif state == WordleLetterState.GREEN:
            if letter not in self.green_letters:
                self.green_letters[letter] = set([])
            self.green_letters[letter].add(position)

    def check(self, word: str) -> bool:
        if len(word) != WORDLE_COLUMNS:
            return False
        for blocked_letter in self.gray_letters:
            if blocked_letter in word:
                return False
        for locked_letter in self.green_letters:
            for required_pos in self.green_letters[locked_letter]:
                if word[required_pos] != locked_letter:
                    return False
        for somewhere_letter in self.yellow_letters:
            for locked_out_pos in self.yellow_letters:
                if word[locked_out_pos] == somewhere_letter:
                    return False
            if somewhere_letter not in word:
                return False
    
        return True
