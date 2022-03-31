from wordle.clue_resolver import (
    check_forcing_guess_filter,
    check_forcing_guess_naive,
    check_forcing_guess_fast,
)
from wordle.word_set_partitioner import required_letter_positions_for_forcing_guess
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

# answer_words = ['choke', 'chose', 'epoch', 'evoke', 'goose', 'noose', 'ozone', 'phone', 'scone', 'scope', 'shone', 'shove', 'spoke', 'whose']
# expected_num_results = 1

# answer_words = ['chili', 'chill', 'icily', 'skill', 'swill']
# expected_num_results = 11

answer_words = [
    'bigot', 'bingo', 'blimp', 'blind', 'blink', 'blitz', 'block', 'blond', 'blood', 'bloom', 'blown', 'bluff', 'blunt', 'bongo', 'booth', 'botch', 'bough', 'bound', 'build', 'built', 'bunch', 'butch', 'buxom', 'chick', 'child', 'chili', 'chill', 'chock', 'chuck', 'chump', 'chunk', 'cinch', 'civic', 'civil', 'click', 'cliff', 'climb', 'cling', 'clink', 'clock', 'cloth', 'cloud', 'clout', 'clown', 'cluck', 'clump', 'clung', 'colon', 'comic', 'conch', 'condo', 'conic', 'couch', 'cough', 'could', 'count', 'cubic', 'cumin', 'digit', 'dingo', 'ditch', 'ditto', 'doing', 'donut', 'doubt', 'dough', 'dutch', 'fifth', 'fight', 'filth', 'finch', 'flick', 'fling', 'flint', 'flock', 'flood', 'flout', 'flown', 'fluff', 'fluid', 'flung', 'flunk', 'folio', 'found', 'fungi', 'ghoul', 'glint', 'gloom', 'going', 'guild', 'guilt', 'gulch', 'gumbo', 'hippo', 'hitch', 'hound', 'humid', 'humph', 'hunch', 'hutch', 'icing', 'idiom', 'idiot', 'igloo', 'inbox', 'ingot', 'input', 'ionic', 'joint', 'jumbo', 'junto', 'knock', 'knoll', 'known', 'light', 'limbo', 'limit', 'lingo', 'lipid', 'livid', 'logic', 'login', 'lucid', 'lunch', 'might', 'mimic', 'minim', 'mogul', 'month', 'motif', 'motto', 'moult', 'mound', 'mount', 'mouth', 'mulch', 'munch', 'night', 'ninth', 'notch', 'onion', 'opium', 'optic', 'ought', 'outdo', 'outgo', 'ovoid', 'owing', 'photo', 'pilot', 'pinch', 'pinto', 'pitch', 'pivot', 'pluck', 'plumb', 'plump', 'plunk', 'point', 'pooch', 'pouch', 'pound', 'pubic', 'punch', 'pupil', 'quick', 'quill', 'quilt', 'quoth', 'thick', 'thigh', 'thing', 'think', 'thong', 'thumb', 'thump', 'tight', 'timid', 'tonic', 'tooth', 'topic', 'touch', 'tough', 'toxic', 'toxin', 'tulip', 'tunic', 'twixt', 'uncut', 'undid', 'unfit', 'union', 'unlit', 'until', 'unzip', 'vigil', 'vivid', 'vomit', 'vouch', 'which', 'whiff', 'whoop', 'widow', 'width', 'wight', 'winch', 'witch', 'would', 'wound'
]
expected_num_results = 0

def forcing_guess_naive_performance():
    results = search_forcing_guesses(check_forcing_guess_naive, answer_words)
    if len(results) != expected_num_results:
        print('unexpected number of forcing guesses from naive:', results)

def forcing_guess_fast_performance():
    results = search_forcing_guesses(check_forcing_guess_fast, answer_words)
    if len(results) != expected_num_results:
        print('unexpected number of forcing guesses from fast:', results)

def search_forcing_guesses_filter(answer_words: List[str]) -> List[str]:
    forcing_guesses = []
    ambiguous_letter_sets = required_letter_positions_for_forcing_guess(answer_words)

    for guess_candidate in guess_wordlist:
        is_forcing_guess = True
        for ambiguous_letters in ambiguous_letter_sets:
            if ambiguous_letters.isdisjoint(guess_candidate):
                # print(
                #     f'guess {guess_candidate.upper()} is not a forcing guess: missing a letter from {ambiguous_letters}'
                # )
                is_forcing_guess = False
                break
        if not is_forcing_guess:
            continue
        is_forcing_guess = check_forcing_guess_naive(guess_candidate, answer_words)
        if is_forcing_guess:
            forcing_guesses.append(guess_candidate)
    return forcing_guesses

def forcing_guess_filter_performance():
    results = search_forcing_guesses_filter(answer_words)
    if len(results) != expected_num_results:
        print('unexpected number of forcing guesses from filter:', results)

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

    print('timing check_forcing_guess_filter...')
    print(
        timeit.timeit(
            "forcing_guess_filter_performance()",
            setup="from __main__ import forcing_guess_filter_performance",
            number=N,
        )
    )
