"""
Given an answer word and a guess, what would the returned clues be?
"""
from wordle.constants import WORDLE_COLUMNS

def _reveal_clues(guess_word: str, answer_word: str) -> str:
    assert len(guess_word) == len(answer_word)
    assert len(guess_word) == WORDLE_COLUMNS

    clue_str = ""
    green_letter_pos = {}
    for idx in range(WORDLE_COLUMNS):
        if answer_word[idx] == guess_word[idx]:
            guess_letter = guess_word[idx]
            if guess_letter not in green_letter_pos:
                green_letter_pos[guess_letter] = set()
            green_letter_pos[guess_letter].add(idx)

    for idx in range(WORDLE_COLUMNS):
        guess_letter = guess_word[idx]
        if guess_letter in answer_word:
            if answer_word[idx] == guess_letter:
                clue_str += 'g'
            else:
                # when the letter in the guess word is also used in a different position that matches the answer word,
                # the letter is marked as green in the correct position, and gray in any incorrect positions.
                if guess_letter in green_letter_pos and idx not in green_letter_pos[guess_letter]:
                    clue_str += 'r'
                else:
                    clue_str += 'y'
        else:
            clue_str += 'r'
    return clue_str