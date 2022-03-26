"""
Given an answer word and a guess, what would the returned clues be?
"""
from typing import List
from tqdm import tqdm

from wordle.constants import WORDLE_COLUMNS

def _reveal_clues(guess_word: str, answer_word: str) -> str:
    # TODO does commenting out these assertions improve performance?
    # assert len(guess_word) == len(answer_word)
    # assert len(guess_word) == WORDLE_COLUMNS

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


def check_forcing_guess_naive(guess_candidate: str, possible_answers: List[str]) -> bool:
    clues_to_answers = {}
    is_forcing_guess = True
    for possible_answer in possible_answers:
        clues = _reveal_clues(guess_candidate, possible_answer)
        if clues in clues_to_answers:
            is_forcing_guess = False
            # if print_debug:
            #     print(f"candidate {guess_candidate} not a forcing guess: {clues_to_answers[clues]} and {possible_answer} are both returned by clue {clues}")
            break
        else:
            clues_to_answers[clues] = set([possible_answer,])
    return is_forcing_guess


def check_forcing_guess_fast(guess_candidate: str, possible_answers: List[str]) -> bool:
    clues_to_answers = {}
    is_forcing_guess = True
    for possible_answer in possible_answers:
        clues = _reveal_clues(guess_candidate, possible_answer)
        if clues in clues_to_answers:
            is_forcing_guess = False
            # if print_debug:
            #     print(f"candidate {guess_candidate} not a forcing guess: {clues_to_answers[clues]} and {possible_answer} are both returned by clue {clues}")
            break
        else:
            clues_to_answers[clues] = set([possible_answer,])
    return is_forcing_guess


def find_forcing_guesses(
    guess_wordlist: List[str],
    possible_answers: List[str],
    return_early: bool = False,
    print_debug: bool = True,
) -> List[str]:
    """
    Returns a list of "forcing guesses". A forcing guess is a guess that can guarantee
    a win on the next guess. In other words, the clues revealed by a forcing guess will
    always narrow down the possible answer words to a single word (or: of all the possible
    answer words, each maps to a different string of clues).
    """
    if len(possible_answers) == 0:
        return []
    if len(possible_answers) <= 2:
        # if there are only 2 possible answer words left, guessing either of them is a forcing guess
        return [guess for guess in possible_answers if guess in guess_wordlist]
    if len(possible_answers) > 243:
        # And note that that if there are more than 3^5 = 243 possible answers, by pigeonhole principle,
        # there is a clue string that is returned by at least two of the possible answer words,
        # so there is no forcing guess
        return []

    if print_debug:
        print("Searching for forcing guesses...")

    forcing_guess_words = []
    for guess_candidate in guess_wordlist:

        is_forcing_guess = check_forcing_guess_naive(guess_candidate, possible_answers)
        if is_forcing_guess:
            forcing_guess_words.append(guess_candidate)
            if return_early:
                return forcing_guess_words

    if len(forcing_guess_words) > 0:
        answer_guesses = [word for word in forcing_guess_words if word in possible_answers]
        if print_debug:
            if len(answer_guesses) > 0:
                print(f"Found forcing guesses that are also possible answers: {answer_guesses}")
                print(f"There are {len(forcing_guess_words)} total forcing guesses")
            else:
                print(f"Found {len(forcing_guess_words)} total forcing guesses: {forcing_guess_words}")
    else:
        if print_debug:
            print("No forcing guesses found")
    return forcing_guess_words

def find_win_in_2_guesses(
    guess_wordlist: List[str],
    possible_answers: List[str],
    return_early: bool = False,
) -> List[str]:
    """
    Look for guesses such that, no matter what the revealed clues are, there is always at least one
    forcing guess. In other words, with optimal play, the guessing player can guarantee a win in
    two more guesses (after guessing one of the words returned by this function).
    """
    print("Searching for guesses that win in 2...")
    win_in_2_guess_words = []
    # TODO add performance benchmarking
    for guess_candidate in tqdm(guess_wordlist):
        clues_to_answers = {}
        for possible_answer in possible_answers:
            clues = _reveal_clues(guess_candidate, possible_answer)
            if clues not in clues_to_answers:
                clues_to_answers[clues] = set()
            clues_to_answers[clues].add(possible_answer)

        is_win_in_2_guess = True
        clues_to_forcing_guesses = {}
        for possible_reveal_clues, next_possible_answers in clues_to_answers.items():
            forcing_guesses = find_forcing_guesses(
                guess_wordlist,
                next_possible_answers,
                return_early=True,
                print_debug=False,
            )
            if len(forcing_guesses) == 0:
                is_win_in_2_guess = False
                break
            else:
                clues_to_forcing_guesses[possible_reveal_clues] = forcing_guesses
        if is_win_in_2_guess:
            win_in_2_guess_words.append(guess_candidate)
            print(f'Found a guess that wins in 2: {guess_candidate}! follow-up forcing guesses:')
            print(clues_to_forcing_guesses)
            if return_early:
                return win_in_2_guess_words

    if len(win_in_2_guess_words) == 0:
        print("No guesses that win in 2 found")
    return win_in_2_guess_words
