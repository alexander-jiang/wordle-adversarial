from wordle_clues import WordleClues, WordleLetterState, ContradictingClue
import pytest


def test_init_clues():
    clues = WordleClues()
    assert clues.check('FIRST')
    assert clues.check('WORST')
    assert clues.check('PRESS')
    assert not clues.check('TOO_LONG_WORD')

def test_full_green_clues():
    clues = WordleClues()
    clues.mark('F', WordleLetterState.GREEN, position=0)
    clues.mark('I', WordleLetterState.GREEN, position=1)
    clues.mark('R', WordleLetterState.GREEN, position=2)
    clues.mark('S', WordleLetterState.GREEN, position=3)
    clues.mark('T', WordleLetterState.GREEN, position=4)
    assert clues.check('FIRST')
    assert not clues.check('WORST') # missing F in position 0 & I in position 1
    assert not clues.check('FOIST') # missing I in position 1 & R in position 2
    assert not clues.check('FIGHT') # missing R in position 2 & S in position 3
    assert not clues.check('FIRMS') # missing S in position 3 & T in position 4

def test_yellow_clues():
    clues = WordleClues()
    clues.mark('T', WordleLetterState.YELLOW, position=0)
    clues.mark('F', WordleLetterState.YELLOW, position=1)
    clues.mark('I', WordleLetterState.YELLOW, position=2)
    clues.mark('R', WordleLetterState.YELLOW, position=3)
    clues.mark('S', WordleLetterState.YELLOW, position=4)
    assert clues.check('FIRST')
    assert not clues.check('RIFTS') # the S cannot be in position 4
    assert not clues.check('WORST') # missing F & I in word
    assert not clues.check('FOIST') # missing R in word
    assert not clues.check('FIGHT') # missing R & S in word
    assert not clues.check('FIRMS') # missing T in word

def test_contradicting_green_clues_same_position():
    """Two different letters cannot be marked as green in the same position."""
    clues = WordleClues()
    clues.mark('F', WordleLetterState.GREEN, position=0)
    clues.mark('R', WordleLetterState.GREEN, position=2)
    clues.mark('S', WordleLetterState.GREEN, position=3)
    clues.mark('T', WordleLetterState.GREEN, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('W', WordleLetterState.GREEN, position=0)
    assert clues.check('FIRST')
    assert not clues.check('WORST') # missing F in position 0

def test_green_clues_same_letter_different_positions():
    """A single letter can be marked as green in multiple positions."""
    clues = WordleClues()
    clues.mark('S', WordleLetterState.GREEN, position=3)
    clues.mark('S', WordleLetterState.GREEN, position=4)
    assert clues.check('DRESS')
    assert clues.check('PRESS')
    assert not clues.check('FIRST') # missing S in position 4

def test_contradicting_yellow_clues_all_positions():
    """
    A letter cannot be marked as yellow in all positions (if it is yellow in all positions,
    then it must appear in the word at some position, but also not in any of the possible positions)
    """
    clues = WordleClues()
    clues.mark('T', WordleLetterState.YELLOW, position=0)
    clues.mark('T', WordleLetterState.YELLOW, position=1)
    clues.mark('T', WordleLetterState.YELLOW, position=2)
    clues.mark('T', WordleLetterState.YELLOW, position=3)
    with pytest.raises(ContradictingClue):
        clues.mark('T', WordleLetterState.YELLOW, position=4)
    assert clues.check('FIRST')
    assert clues.check('WORST')
    assert not clues.check('DRESS') # missing T in word
    assert not clues.check('TRYST') # the T cannot be in position 0


def test_contradicting_yellow_clues_all_non_green_positions():
    """
    A letter cannot be marked as yellow in all positions that do not have a different green letter
    (if it is yellow in all of those positions, then it must appear in the word at some position,
    but also not in any of the possible positions, as the remaining positions must be filled by a different
    letter due to the green clue)
    """
    clues = WordleClues()
    clues.mark('F', WordleLetterState.GREEN, position=0)
    clues.mark('I', WordleLetterState.GREEN, position=1)
    clues.mark('T', WordleLetterState.YELLOW, position=2)
    clues.mark('T', WordleLetterState.YELLOW, position=3)
    with pytest.raises(ContradictingClue):
        clues.mark('T', WordleLetterState.YELLOW, position=4)
    assert clues.check('FIRST')
    assert clues.check('FIGHT')
    assert not clues.check('WORST') # missing F in position 0 & I in position 1
    assert not clues.check('FIRES') # missing T in word
    assert not clues.check('FITLY') # the T cannot be in position 2

# TODO (can test contradicting gray clues: there must be at least one non-gray letter)
# TODO and if there are 5 different yellow letters, then no other letters can be yellow or green (only at most 5 letters in the word)

def test_yellow_and_green_clues():
    """
    A letter can be marked as yellow in all non-green positions if there is a green position
    for the same letter.
    """
    clues = WordleClues()
    clues.mark('F', WordleLetterState.GREEN, position=0)
    clues.mark('I', WordleLetterState.GREEN, position=1)
    clues.mark('F', WordleLetterState.YELLOW, position=2)
    clues.mark('F', WordleLetterState.YELLOW, position=3)
    clues.mark('F', WordleLetterState.YELLOW, position=4)
    assert clues.check('FIRST')
    assert clues.check('FIGHT')
    assert clues.check('FILCH')
    assert not clues.check('FETCH') # missing I in position 1
    assert not clues.check('PITCH') # missing F in position 0
    assert not clues.check('FIEFS') # the F cannot be in position 3