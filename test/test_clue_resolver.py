from wordle.clue_resolver import _reveal_clues, find_forcing_guesses
from wordle.word_list_searcher import _read_words_from_file
import pytest

def test_answer_caulk():
    answer_word = 'caulk'
    assert _reveal_clues('grail', answer_word) == 'rryry'
    assert _reveal_clues('aleph', answer_word) == 'yyrrr'
    assert _reveal_clues('lauds', answer_word) == 'yggrr'
    assert _reveal_clues('combs', answer_word) == 'grrrr'
    assert _reveal_clues('caulk', answer_word) == 'ggggg'

def test_answer_shake():
    answer_word = 'shake'
    assert _reveal_clues('sloth', answer_word) == 'grrry'
    assert _reveal_clues('share', answer_word) == 'gggrg'
    assert _reveal_clues('dumpy', answer_word) == 'rrrrr'
    assert _reveal_clues('shake', answer_word) == 'ggggg'

def test_answer_dodge():
    answer_word = 'dodge'
    assert _reveal_clues('raven', answer_word) == 'rrryr'
    assert _reveal_clues('eight', answer_word) == 'yryrr'
    assert _reveal_clues('gulps', answer_word) == 'yrrrr'
    assert _reveal_clues('dodge', answer_word) == 'ggggg'

def test_answer_swill():
    answer_word = 'swill'
    assert _reveal_clues('drape', answer_word) == 'rrrrr'
    assert _reveal_clues('built', answer_word) == 'rrggr'
    assert _reveal_clues('jocks', answer_word) == 'rrrry'
    assert _reveal_clues('swill', answer_word) == 'ggggg'

def test_answer_tacit():
    answer_word = 'tacit'
    assert _reveal_clues('waltz', answer_word) == 'rgryr'
    assert _reveal_clues('miter', answer_word) == 'ryyrr'
    assert _reveal_clues('scout', answer_word) == 'ryrrg'
    assert _reveal_clues('tacit', answer_word) == 'ggggg'

    assert _reveal_clues('waltz', answer_word) == 'rgryr'
    assert _reveal_clues('taker', answer_word) == 'ggrrr'
    assert _reveal_clues('tapas', answer_word) == 'ggrrr'
    assert _reveal_clues('tangy', answer_word) == 'ggrrr'
    assert _reveal_clues('taboo', answer_word) == 'ggrrr'
    assert _reveal_clues('tacit', answer_word) == 'ggggg'

def test_answer_other():
    answer_word = 'other'
    assert _reveal_clues('heart', answer_word) == 'yyryy'
    assert _reveal_clues('ether', answer_word) == 'rgggg'
    assert _reveal_clues('other', answer_word) == 'ggggg'

def test_answer_thorn():
    answer_word = 'thorn'
    assert _reveal_clues('argue', answer_word) == 'ryrrr'
    assert _reveal_clues('storm', answer_word) == 'ryggr'
    assert _reveal_clues('thorn', answer_word) == 'ggggg'

    assert _reveal_clues('argue', answer_word) == 'ryrrr'
    assert _reveal_clues('rhino', answer_word) == 'ygryy'
    assert _reveal_clues('shorn', answer_word) == 'rgggg'
    assert _reveal_clues('thorn', answer_word) == 'ggggg'

def test_answer_trove():
    answer_word = 'trove'
    assert _reveal_clues('feint', answer_word) == 'ryrry'
    assert _reveal_clues('trade', answer_word) == 'ggrrg'
    assert _reveal_clues('pouch', answer_word) == 'ryrrr'
    assert _reveal_clues('trove', answer_word) == 'ggggg'

def test_guess_ether():
    guess_word = 'ether'
    assert _reveal_clues(guess_word, 'ether') == 'ggggg'
    assert _reveal_clues(guess_word, 'other') == 'rgggg'
    assert _reveal_clues(guess_word, 'their') == 'yyyyg'
    assert _reveal_clues(guess_word, 'three') == 'yyygy'
    assert _reveal_clues(guess_word, 'threw') == 'ryygy'

def test_answer_bloke():
    answer_word = 'bloke'
    assert _reveal_clues('unite', answer_word) == 'rrrrg'
    assert _reveal_clues('polar', answer_word) == 'ryyrr'
    assert _reveal_clues('close', answer_word) == 'rggrg'
    assert _reveal_clues('glove', answer_word) == 'rggrg'
    assert _reveal_clues('bloke', answer_word) == 'ggggg'

def test_answer_vivid():
    answer_word = 'vivid'
    assert _reveal_clues('years', answer_word) == 'rrrrr'
    assert _reveal_clues('odium', answer_word) == 'ryyrr'
    assert _reveal_clues('dight', answer_word) == 'ygrrr'
    assert _reveal_clues('lucid', answer_word) == 'rrrgg'
    assert _reveal_clues('vivid', answer_word) == 'ggggg'

def test_answer_spill():
    answer_word = 'spill'
    assert _reveal_clues('thick', answer_word) == 'rrgrr'
    assert _reveal_clues('learn', answer_word) == 'yrrrr'
    assert _reveal_clues('fouls', answer_word) == 'rrrgy'
    assert _reveal_clues('sibyl', answer_word) == 'gyrrg'
    assert _reveal_clues('spill', answer_word) == 'ggggg'

def test_answer_rupee():
    answer_word = 'rupee'
    assert _reveal_clues('arose', answer_word) == 'ryrrg'
    assert _reveal_clues('purge', answer_word) == 'ygyrg'
    assert _reveal_clues('rupee', answer_word) == 'ggggg'

    assert _reveal_clues('arose', answer_word) == 'ryrrg'
    assert _reveal_clues('lurid', answer_word) == 'rgyrr'
    assert _reveal_clues('rupee', answer_word) == 'ggggg'

def test_answer_choke():
    answer_word = 'choke'
    assert _reveal_clues('broil', answer_word) == 'rrgrr'
    assert _reveal_clues('meaty', answer_word) == 'ryrrr'
    assert _reveal_clues('fudge', answer_word) == 'rrrrg'
    assert _reveal_clues('chose', answer_word) == 'gggrg'
    assert _reveal_clues('choke', answer_word) == 'ggggg'

def test_answer_nasty():
    answer_word = 'nasty'
    assert _reveal_clues('smart', answer_word) == 'yryry'
    assert _reveal_clues('tails', answer_word) == 'ygrry'
    assert _reveal_clues('bench', answer_word) == 'rryrr'
    assert _reveal_clues('nasty', answer_word) == 'ggggg'

def test_forcing_guess():
    guess_wordlist_path = '3b1b-data/allowed_words.txt'
    guess_wordlist = _read_words_from_file(guess_wordlist_path)

    # Can distinguish between CHILL and CHILI, or SKILL and SWILL
    answer_words = ['chili', 'chill', 'icily', 'skill', 'swill']
    assert set(['cowal', 'crawl', 'kahal', 'scowl', 'shawl', 'swayl', 'thowl', 'wheal', 'wheel', 'whirl', 'whorl']) == set(find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    ))

    answer_words = ['shade', 'shake', 'shame', 'shape', 'shave']
    assert len(find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    )) == 0

    answer_words = ['faint', 'habit', 'paint', 'saint', 'tacit', 'taint']
    assert set(['tapis', 'tipis', 'topis', 'trips']) == set(find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    ))

    answer_words = ['bloke', 'close', 'clove', 'globe', 'glove', 'whole']
    assert 'clubs' in find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    )

    answer_words = ['digit', 'ditch', 'lipid', 'livid', 'vivid', 'width']
    assert 'devil' in find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    )

    answer_words = ['choke', 'chose', 'epoch', 'evoke', 'goose', 'noose', 'ozone', 'phone', 'scone', 'scope', 'shone', 'shove', 'spoke', 'whose']
    assert ['synch'] == find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=False,
    )

    # Can distinguish between THREE and THREW by guessing an E outside of the 4th position
    answer_words = ['ether', 'other', 'their', 'three', 'threw']
    forcing_guesses = find_forcing_guesses(
        guess_wordlist,
        possible_answers=answer_words,
        return_early=False,
        print_debug=True,
    )
    assert 'ether' in forcing_guesses and 'three' in forcing_guesses