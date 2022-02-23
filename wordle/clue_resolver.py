"""
Given an answer word and a guess, what would the returned clues be?
"""
from wordle.constants import WORDLE_COLUMNS

def _reveal_clues(guess_word: str, answer_word: str) -> str:
    assert len(guess_word) == len(answer_word)
    assert len(guess_word) == WORDLE_COLUMNS

    clues_by_pos = [None for _i in range(WORDLE_COLUMNS)]
    correct_positions = [False for _i in range(WORDLE_COLUMNS)]
    for idx in range(WORDLE_COLUMNS):
        if answer_word[idx] == guess_word[idx]:
            clues_by_pos[idx] = 'g'
            correct_positions[idx] = True

    for idx in range(WORDLE_COLUMNS):
        if clues_by_pos[idx] is not None:
            continue
        guess_letter = guess_word[idx]
        if guess_letter not in answer_word:
            clues_by_pos[idx] = 'r'
            continue
        
        # the letter is present in the answer word (and not at the current index), 
        # but the other instance of this letter already accounted for by a correct/green guess?
        for j in range(WORDLE_COLUMNS):
            if answer_word[j] == guess_letter and not correct_positions[j]:
                # there is an occurrence of `guess_letter` that is not accounted for by the correct/green positions
                clues_by_pos[idx] = 'y'
                break
        if clues_by_pos[idx] is None:
            clues_by_pos[idx] = 'r'

    return "".join(clues_by_pos)