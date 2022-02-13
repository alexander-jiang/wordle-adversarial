"""
Representation of the information gathered in a Wordle game
(i.e. which letters are colored gray, which are colored yellow 
or green, and the remaining letters with no information)
"""
from abc import ABC, abstractmethod
from enum import Enum
from constants import WORDLE_COLUMNS
from typing import MutableSet, List, Optional
import numpy as np


class WordleLetterState(Enum):
    GRAY = -1
    NO_INFO = 0
    YELLOW = 1
    GREEN = 2


class ContradictingClue(Exception):
    pass


def _extract_set_positions(packed_value: int) -> List[int]:
    """Returns a list of positions with set bits from the packed value in little endian"""
    return [i for i in range(WORDLE_COLUMNS) if packed_value & (1 << i)]

def _extract_clear_positions(packed_value: int) -> List[int]:
    """Returns a list of positions with clear bits from the packed value in little endian"""
    return [i for i in range(WORDLE_COLUMNS) if (~packed_value & 63) & (1 << i)]

def _letter_idx_to_str(letter_idx: int) -> str:
    return chr(ord("A") + letter_idx)

def _letter_str_to_idx(letter: str) -> int:
    return ord(letter) - ord("A")

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

        # a 26x5 bitarray: each row corresponds to a letter, and each column to a position
        # but each row of bits is packed into a 26-element array using little endian (e.g. bit
        # corresponding to position 0 is the least significant bit)
        # for each letter marked yellow, the row contains a bitmask, the letter must appear in
        # *at least one* of the positions indicated by the cleared bits
        self.yellow_letters = np.zeros((26, 5))
        self.yellow_packed_by_letter = [0 for _i in range(26)]

        # a list of letters that are marked as yellow in each position
        self.yellow_by_position: List[MutableSet[str]] = [set([]) for _i in range(5)]

        # as above, a 26x5 bitarray of (letter x position) packed into a 26-element array
        # for each letter marked green, the row contains a bitmask where the letter must appear in
        # *all* positions indicated by the set bits
        self.green_letters = np.zeros((26, 5))
        self.green_packed_by_letter = [0 for _i in range(26)]

        # letters that are marked as green in each position
        self.green_by_position: List[Optional[str]] = [None for _i in range(5)]


    def mark(self, letter: str, state: WordleLetterState, position: int) -> None:
        assert len(letter) == 1 and ord("A") <= ord(letter) <= ord(
            "Z"
        ), f"WordleClues.mark() must be called with a string containing a single upper-case letter, was instead called with {letter}"
        assert state in [
            WordleLetterState.NO_INFO,
            WordleLetterState.GRAY,
            WordleLetterState.YELLOW,
            WordleLetterState.GREEN,
        ], f"WordleClues.mark() must be called with valid state, was instead called with {position}"
        assert (
            0 <= position < WORDLE_COLUMNS
        ), f"WordleClues.mark() must be called with position between 0 and {WORDLE_COLUMNS - 1}, was instead called with {position}"
        if state == WordleLetterState.NO_INFO:
            # Clear the data structures
            self.gray_letters.remove(letter)
            self.yellow_letters[position] = 0
            self.green_letters[position] = 0
        elif state == WordleLetterState.GRAY:
            if len(self.gray_letters) == 25 and letter not in self.gray_letters:
                raise ContradictingClue('Cannot have all 26 letters be gray')
            self.gray_letters.add(letter)
        elif state == WordleLetterState.YELLOW:
            letter_idx = _letter_str_to_idx(letter)
            # TODO check for contradicting yellow clues: must be at least one non-set bit that isn't in a position with a green
            self.yellow_letters[letter_idx, position] = 1
            self.yellow_packed_by_letter[letter_idx] ^= 1 << position
        elif state == WordleLetterState.GREEN:
            green_in_position = self.green_by_position[position]
            if green_in_position != letter:
                if green_in_position is not None:
                    raise ContradictingClue(f'Letter {green_in_position} is already green in position {position}, cannot also have letter {letter} green in the same position')
                letter_idx = _letter_str_to_idx(letter)
                self.green_letters[letter_idx, position] = 1
                self.green_packed_by_letter[letter_idx] ^= 1 << position
                self.green_by_position[position] = letter

    def check(self, word: str) -> bool:
        if len(word) != WORDLE_COLUMNS:
            return False
        for blocked_letter in self.gray_letters:
            if blocked_letter in word:
                return False
        for letter_idx in range(len(self.green_letters)):
            if self.green_packed_by_letter[letter_idx] == 0:
                continue
            locked_letter = _letter_idx_to_str(letter_idx)
            required_positions = _extract_set_positions(self.green_packed_by_letter[letter_idx])
            # print(f'required positions for letter {locked_letter}: {required_positions}')
            for required_pos in required_positions:
                if word[required_pos] != locked_letter:
                    return False
        for letter_idx in range(len(self.yellow_letters)):
            if self.yellow_packed_by_letter[letter_idx] == 0:
                continue
            somewhere_letter = _letter_idx_to_str(letter_idx)
            allowed_positions = _extract_clear_positions(self.yellow_packed_by_letter[letter_idx])
            # print(f'letter {somewhere_letter} must appear in only these positions {allowed_positions}')
            found = False
            for position in range(WORDLE_COLUMNS):
                if word[position] == somewhere_letter:
                    if position not in allowed_positions:
                        return False
                    else:
                        found = True
            if not found:
                return False

        return True
