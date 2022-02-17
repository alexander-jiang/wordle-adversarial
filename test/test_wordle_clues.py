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
    assert not clues.check('RIFTS') # S cannot be in position 4
    assert not clues.check('WORST') # missing F & I in word
    assert not clues.check('FOIST') # missing R in word
    assert not clues.check('FIGHT') # missing R & S in word
    assert not clues.check('FIRMS') # missing T in word

def test_gray_clues():
    clues = WordleClues()
    clues.mark('W', WordleLetterState.GRAY, position=2)
    clues.mark('O', WordleLetterState.GRAY, position=2)
    assert clues.check('FIRST')
    assert clues.check('FIGHT')
    assert clues.check('FIRMS')
    assert not clues.check('WORST') # letter W is gray (position of gray clue doesn't matter)
    assert not clues.check('FOIST') # letter O is gray


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

def test_contradicting_green_yellow_clues_same_letter_position():
    """A single letter cannot be marked as both green and yellow in the same position."""
    clues = WordleClues()
    clues.mark('E', WordleLetterState.GREEN, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('E', WordleLetterState.YELLOW, position=0)
    clues.mark('E', WordleLetterState.YELLOW, position=1)
    assert clues.check('ELITE')
    assert not clues.check('WORST') # missing E in position 0
    assert not clues.check('EERIE') # E cannot be in position 1

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
    assert not clues.check('TRYST') # T cannot be in position 0


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
    assert not clues.check('FILTH') # T cannot be in position 3

def test_contradicting_gray_clues_need_one_non_gray_letter():
    """There must be at least one non-gray letter"""
    clues = WordleClues()
    for letter_ord in range(ord("A"), ord("Y") + 1):
        letter = chr(letter_ord)
        clues.mark(letter, WordleLetterState.GRAY, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('Z', WordleLetterState.GRAY, position=0)
    assert clues.check('ZZZZZ')
    assert not clues.check('WORST') # letters A-Y are gray
    assert not clues.check('FIRES') # letters A-Y are gray
    assert not clues.check('FILTH') # letters A-Y are gray

def test_contradicting_clues_six_yellow_letters():
    clues = WordleClues()
    clues.mark('T', WordleLetterState.YELLOW, position=0)
    clues.mark('F', WordleLetterState.YELLOW, position=1)
    clues.mark('S', WordleLetterState.YELLOW, position=2)
    clues.mark('I', WordleLetterState.YELLOW, position=3)
    clues.mark('R', WordleLetterState.YELLOW, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('E', WordleLetterState.YELLOW, position=0)
    assert clues.check('FIRST')
    assert not clues.check('FIRES') # missing T in word

# TODO test: there cannot be >5 yellow or green letters (only at most 5 letters in the word), but there can be <5 yellow or green (if answer word uses a letter multiple times)
def test_contradicting_clues_six_yellow_or_green_letters():
    clues = WordleClues()
    clues.mark('S', WordleLetterState.YELLOW, position=0)
    clues.mark('I', WordleLetterState.GREEN, position=1)
    clues.mark('F', WordleLetterState.YELLOW, position=2)
    clues.mark('R', WordleLetterState.YELLOW, position=3)
    clues.mark('T', WordleLetterState.GREEN, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('E', WordleLetterState.GREEN, position=3)
    assert clues.check('FIRST')
    assert not clues.check('FISTS') # missing R in word


def test_contradicting_clues_five_yellow_letters_same_position():
    """There can't be >4 letters that are yellow in same position"""
    clues = WordleClues()
    clues.mark('T', WordleLetterState.YELLOW, position=0)
    clues.mark('I', WordleLetterState.YELLOW, position=0)
    clues.mark('S', WordleLetterState.YELLOW, position=0)
    clues.mark('R', WordleLetterState.YELLOW, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('F', WordleLetterState.YELLOW, position=0)
    # but having the 5th letter be yellow in different position is allowed
    clues.mark('F', WordleLetterState.YELLOW, position=1)
    clues.mark('F', WordleLetterState.YELLOW, position=2)
    assert clues.check('FIRST')
    assert not clues.check('STIRS') # S cannot be in position 0

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
    assert not clues.check('FIEFS') # F cannot be in position 3