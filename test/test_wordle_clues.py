from wordle.wordle_clues import WordleClues, WordleLetterState, ContradictingClue
import pytest


def test_init_clues():
    clues = WordleClues()
    assert clues.check('first')
    assert clues.check('worst')
    assert clues.check('press')
    assert not clues.check('too_long_word')

def test_full_green_clues():
    clues = WordleClues()
    clues.mark('f', WordleLetterState.GREEN, position=0)
    clues.mark('i', WordleLetterState.GREEN, position=1)
    clues.mark('r', WordleLetterState.GREEN, position=2)
    clues.mark('s', WordleLetterState.GREEN, position=3)
    clues.mark('t', WordleLetterState.GREEN, position=4)
    assert clues.check('first')
    assert not clues.check('worst') # missing F in position 0 & I in position 1
    assert not clues.check('foist') # missing I in position 1 & R in position 2
    assert not clues.check('fight') # missing R in position 2 & S in position 3
    assert not clues.check('firms') # missing S in position 3 & T in position 4

def test_yellow_clues():
    clues = WordleClues()
    clues.mark('t', WordleLetterState.YELLOW, position=0)
    clues.mark('f', WordleLetterState.YELLOW, position=1)
    clues.mark('i', WordleLetterState.YELLOW, position=2)
    clues.mark('r', WordleLetterState.YELLOW, position=3)
    clues.mark('s', WordleLetterState.YELLOW, position=4)
    assert clues.check('first')
    assert not clues.check('rifts') # S cannot be in position 4
    assert not clues.check('worst') # missing F & I in word
    assert not clues.check('foist') # missing R in word
    assert not clues.check('fight') # missing R & S in word
    assert not clues.check('firms') # missing T in word

def test_gray_clues():
    clues = WordleClues()
    clues.mark('w', WordleLetterState.GRAY, position=2)
    clues.mark('o', WordleLetterState.GRAY, position=2)
    assert clues.check('first')
    assert clues.check('fight')
    assert clues.check('firms')
    assert not clues.check('worst') # letter W is gray (position of gray clue doesn't matter)
    assert not clues.check('foist') # letter O is gray


def test_contradicting_green_clues_same_position():
    """Two different letters cannot be marked as green in the same position."""
    clues = WordleClues()
    clues.mark('f', WordleLetterState.GREEN, position=0)
    clues.mark('r', WordleLetterState.GREEN, position=2)
    clues.mark('s', WordleLetterState.GREEN, position=3)
    clues.mark('t', WordleLetterState.GREEN, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('w', WordleLetterState.GREEN, position=0)
    assert clues.check('first')
    assert not clues.check('worst') # missing F in position 0

def test_contradicting_green_yellow_clues_same_letter_position():
    """A single letter cannot be marked as both green and yellow in the same position."""
    clues = WordleClues()
    clues.mark('e', WordleLetterState.GREEN, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('e', WordleLetterState.YELLOW, position=0)
    clues.mark('e', WordleLetterState.YELLOW, position=1)
    assert clues.check('elite')
    assert not clues.check('worst') # missing E in position 0
    assert not clues.check('eerie') # E cannot be in position 1

def test_green_clues_same_letter_different_positions():
    """A single letter can be marked as green in multiple positions."""
    clues = WordleClues()
    clues.mark('s', WordleLetterState.GREEN, position=3)
    clues.mark('s', WordleLetterState.GREEN, position=4)
    assert clues.check('dress')
    assert clues.check('press')
    assert not clues.check('first') # missing S in position 4

def test_contradicting_yellow_clues_all_positions():
    """
    A letter cannot be marked as yellow in all positions (if it is yellow in all positions,
    then it must appear in the word at some position, but also not in any of the possible positions)
    """
    clues = WordleClues()
    clues.mark('t', WordleLetterState.YELLOW, position=0)
    clues.mark('t', WordleLetterState.YELLOW, position=1)
    clues.mark('t', WordleLetterState.YELLOW, position=2)
    clues.mark('t', WordleLetterState.YELLOW, position=3)
    with pytest.raises(ContradictingClue):
        clues.mark('t', WordleLetterState.YELLOW, position=4)
    assert clues.check('first')
    assert clues.check('worst')
    assert not clues.check('dress') # missing T in word
    assert not clues.check('tryst') # T cannot be in position 0


def test_contradicting_yellow_clues_all_non_green_positions():
    """
    A letter cannot be marked as yellow in all positions that do not have a different green letter
    (if it is yellow in all of those positions, then it must appear in the word at some position,
    but also not in any of the possible positions, as the remaining positions must be filled by a different
    letter due to the green clue)
    """
    clues = WordleClues()
    clues.mark('f', WordleLetterState.GREEN, position=0)
    clues.mark('i', WordleLetterState.GREEN, position=1)
    clues.mark('t', WordleLetterState.YELLOW, position=2)
    clues.mark('t', WordleLetterState.YELLOW, position=3)
    with pytest.raises(ContradictingClue):
        clues.mark('t', WordleLetterState.YELLOW, position=4)
    assert clues.check('first')
    assert clues.check('fight')
    assert not clues.check('worst') # missing F in position 0 & I in position 1
    assert not clues.check('fires') # missing T in word
    assert not clues.check('filth') # T cannot be in position 3

def test_contradicting_gray_clues_need_one_non_gray_letter():
    """There must be at least one non-gray letter"""
    clues = WordleClues()
    for letter_ord in range(ord('a'), ord('y') + 1):
        letter = chr(letter_ord)
        clues.mark(letter, WordleLetterState.GRAY, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('z', WordleLetterState.GRAY, position=0)
    assert clues.check('zzzzz')
    assert not clues.check('worst') # letters A-Y are gray
    assert not clues.check('fires') # letters A-Y are gray
    assert not clues.check('filth') # letters A-Y are gray

def test_contradicting_clues_six_yellow_letters():
    clues = WordleClues()
    clues.mark('t', WordleLetterState.YELLOW, position=0)
    clues.mark('f', WordleLetterState.YELLOW, position=1)
    clues.mark('s', WordleLetterState.YELLOW, position=2)
    clues.mark('i', WordleLetterState.YELLOW, position=3)
    clues.mark('r', WordleLetterState.YELLOW, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('e', WordleLetterState.YELLOW, position=0)
    assert clues.check('first')
    assert not clues.check('fires') # missing T in word

# TODO test: there cannot be >5 yellow or green letters (only at most 5 letters in the word), but there can be <5 yellow or green (if answer word uses a letter multiple times)
def test_contradicting_clues_six_yellow_or_green_letters():
    clues = WordleClues()
    clues.mark('s', WordleLetterState.YELLOW, position=0)
    clues.mark('i', WordleLetterState.GREEN, position=1)
    clues.mark('f', WordleLetterState.YELLOW, position=2)
    clues.mark('r', WordleLetterState.YELLOW, position=3)
    clues.mark('t', WordleLetterState.GREEN, position=4)
    with pytest.raises(ContradictingClue):
        clues.mark('e', WordleLetterState.GREEN, position=3)
    assert clues.check('first')
    assert not clues.check('fists') # missing R in word


def test_contradicting_clues_five_yellow_letters_same_position():
    """There can't be >4 letters that are yellow in same position"""
    clues = WordleClues()
    clues.mark('t', WordleLetterState.YELLOW, position=0)
    clues.mark('i', WordleLetterState.YELLOW, position=0)
    clues.mark('s', WordleLetterState.YELLOW, position=0)
    clues.mark('r', WordleLetterState.YELLOW, position=0)
    with pytest.raises(ContradictingClue):
        clues.mark('f', WordleLetterState.YELLOW, position=0)
    # but having the 5th letter be yellow in different position is allowed
    clues.mark('f', WordleLetterState.YELLOW, position=1)
    clues.mark('f', WordleLetterState.YELLOW, position=2)
    assert clues.check('first')
    assert not clues.check('stirs') # S cannot be in position 0

def test_yellow_and_green_clues():
    """
    A letter can be marked as yellow in all non-green positions if there is a green position
    for the same letter.
    """
    clues = WordleClues()
    clues.mark('f', WordleLetterState.GREEN, position=0)
    clues.mark('i', WordleLetterState.GREEN, position=1)
    clues.mark('f', WordleLetterState.YELLOW, position=2)
    clues.mark('f', WordleLetterState.YELLOW, position=3)
    clues.mark('f', WordleLetterState.YELLOW, position=4)
    assert clues.check('first')
    assert clues.check('fight')
    assert clues.check('filch')
    assert not clues.check('fetch') # missing I in position 1
    assert not clues.check('pitch') # missing F in position 0
    assert not clues.check('fiefs') # F cannot be in position 3