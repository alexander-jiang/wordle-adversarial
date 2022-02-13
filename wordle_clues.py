"""
Representation of the information gathered in a Wordle game
(i.e. which letters are colored gray, which are colored yellow 
or green, and the remaining letters with no information)
"""
from abc import ABC, abstractmethod
from enum import Enum
from constants import WORDLE_COLUMNS
from typing import MutableSet, List, Optional, Dict


class WordleLetterState(Enum):
    GRAY = -1
    NO_INFO = 0
    YELLOW = 1
    GREEN = 2


class ContradictingClue(Exception):
    pass


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
        self.gray_letters: MutableSet[str] = set()

        # used in check() method:
        # a set of letters that have been marked as yellow (must appear in the word at some position)
        self.yellow_letters_set: MutableSet[str] = set()
        # a list of letters that are marked as yellow in each position
        self.yellow_by_position: List[MutableSet[str]] = [set() for _i in range(5)]

        # used in check() method:
        # map from letter to set of all positions (0-indexed) where that letter must appear in the word
        self.green_letter_positions: Dict[str, MutableSet[int]] = {}

        # used to detect contradicting clues in mark() method:
        # for each position (0-indexed), the letter (if any) that is marked as green in that position
        self.green_by_position: List[Optional[str]] = [None for _i in range(5)]


    def mark(self, letter: str, state: WordleLetterState, position: int) -> None:
        assert len(letter) == 1 and ord("A") <= ord(letter) <= ord(
            "Z"
        ), f"WordleClues.mark() expects a string containing a single upper-case letter, was instead called with {letter}"
        assert state in [
            WordleLetterState.GRAY,
            WordleLetterState.YELLOW,
            WordleLetterState.GREEN,
        ], f"WordleClues.mark() expects a valid state, was instead called with {state}"
        assert (
            0 <= position < WORDLE_COLUMNS
        ), f"WordleClues.mark() expects a position between 0 and {WORDLE_COLUMNS - 1}, was instead called with {position}"
        if state == WordleLetterState.GRAY:
            if len(self.gray_letters) == 25 and letter not in self.gray_letters:
                raise ContradictingClue('Cannot have all 26 letters be gray')
            self.gray_letters.add(letter)
        elif state == WordleLetterState.YELLOW:
            # TODO check for contradicting yellow clues: must be at least one non-set bit that isn't in a position with a green
            self.yellow_letters_set.add(letter)
            self.yellow_by_position[position].add(letter)
        elif state == WordleLetterState.GREEN:
            green_in_position = self.green_by_position[position]
            if green_in_position != letter:
                if green_in_position is not None:
                    raise ContradictingClue(f'Letter {green_in_position} is already green in position {position}, cannot also have letter {letter} green in the same position')

                if letter not in self.green_letter_positions:
                    self.green_letter_positions[letter] = set()
                self.green_letter_positions[letter].add(position)
                self.green_by_position[position] = letter

    # note: should optimize for the efficiency of check (i.e. do precomputing in mark(), but make check() as fast as possible,
    # to quickly search through word lists)
    def check(self, word: str) -> bool:
        if len(word) != WORDLE_COLUMNS:
            return False

        # TODO - is it worth converting the word (list of chars) to a set of chars? or a letter count map?
        # to optimize performance of "in word" / "not in word" conditions

        for gray_letter in self.gray_letters:
            if gray_letter in word:
                print(f'gray letter {gray_letter} cannot appear in the word')
                return False

        for green_letter, required_positions in self.green_letter_positions.items():
            for required_pos in required_positions:
                if word[required_pos] != green_letter:
                    print(f'green letter {green_letter} does not appear in position {required_pos}')
                    return False

        for yellow_letter in self.yellow_letters_set:
            if yellow_letter not in word:
                print(f'yellow letter {yellow_letter} must appear in the word')
                return False
        for position in range(WORDLE_COLUMNS):
            if word[position] in self.yellow_by_position[position]:
                print(f'letter {word[position]} is marked yellow at position {position}')
                return False

        return True
