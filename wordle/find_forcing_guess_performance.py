from wordle.clue_resolver import (
    check_forcing_guess_naive,
    check_forcing_guess_fast,
)
from wordle.word_list_searcher import _read_words_from_file
import timeit
from typing import List

guess_wordlist_path = '3b1b-data/allowed_words.txt'
guess_wordlist = _read_words_from_file(guess_wordlist_path)
def search_forcing_guesses(check_func, answer_words: List[str]) -> List[str]:
    forcing_guesses = []
    for guess_candidate in guess_wordlist:
        is_forcing_guess = check_func(guess_candidate, answer_words)
        if is_forcing_guess:
            forcing_guesses.append(guess_candidate)
    return forcing_guesses

answer_words = ['choke', 'chose', 'epoch', 'evoke', 'goose', 'noose', 'ozone', 'phone', 'scone', 'scope', 'shone', 'shove', 'spoke', 'whose']

def forcing_guess_naive_performance():
    search_forcing_guesses(check_forcing_guess_naive, answer_words)

def forcing_guess_fast_performance():
    search_forcing_guesses(check_forcing_guess_fast, answer_words)

if __name__ == '__main__':
    N = 100
    print('timing check_forcing_guess_naive...')
    print(
        timeit.timeit(
            "forcing_guess_naive_performance()",
            setup="from __main__ import forcing_guess_naive_performance",
            number=N,
        )
    )

    print('timing check_forcing_guess_fast...')
    print(
        timeit.timeit(
            "forcing_guess_fast_performance()",
            setup="from __main__ import forcing_guess_fast_performance",
            number=N,
        )
    )