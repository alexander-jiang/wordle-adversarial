"""
Given a set of possible answer words, what is the best way to
partition the words? based on things like letter frequency, letter combos,
letter-position frequency, etc.
"""
import click
import itertools
from typing import List, Dict

from wordle.word_list_searcher import WordListSearcher, _read_words_from_file
from wordle.constants import WORDLE_COLUMNS, ALPHABET


def partition(words: List[str]):
    letter_freqs = {}
    for letter_ord in range(ord("a"), ord("z") + 1):
        letter = chr(letter_ord)
        letter_freqs[letter] = 0
    for word in words:
        word_letters = set([word[idx] for idx in range(WORDLE_COLUMNS)])
        for letter in word_letters:
            letter_freqs[letter] += 1

    differentiating_letters = []
    for letter_ord in range(ord("a"), ord("z") + 1):
        letter = chr(letter_ord)
        if letter_freqs[letter] != 0 and letter_freqs[letter] != len(words):
            differentiating_letters.append(letter)

    print(f"of {len(words)} words, these are ambiguous letter frequencies:")
    letter_freq_kvs = [
        (letter, letter_freqs[letter])
        for letter in letter_freqs
        if letter_freqs[letter] != 0 and letter_freqs[letter] != len(words)
    ]
    sorted_freq_kvs = sorted(letter_freq_kvs, key=lambda kv: kv[1], reverse=True)
    print(sorted_freq_kvs)
    return differentiating_letters


def pick_narrowing_guesses_by_letters(letters: List[str], guess_wordlist: List[str]):
    best_guesses = []
    max_letters_covered = 0
    for candidate in guess_wordlist:
        letters_in_candidate = [letter for letter in letters if letter in candidate]
        if len(letters_in_candidate) > max_letters_covered:
            max_letters_covered = len(letters_in_candidate)
            best_guesses = [candidate]
        elif len(letters_in_candidate) == max_letters_covered:
            best_guesses.append(candidate)
    return best_guesses, max_letters_covered


def generate_similar_word_answer_sets(answer_wordlist: List[str]):
    word_patterns: Dict[str, List[str]] = {}
    for answer_word in answer_wordlist:
        for idx in range(WORDLE_COLUMNS):
            word_pattern_key = answer_word[:idx] + "_" + answer_word[idx + 1 :]
            if word_pattern_key not in word_patterns:
                word_patterns[word_pattern_key] = []
            word_patterns[word_pattern_key].append(answer_word)
    return word_patterns


@click.command()
@click.option(
    "--guess-wordlist-path",
    "-g",
    type=str,
    default="3b1b-data/allowed_words.txt",
    help="path to a text file where each valid guess word is on its own line",
)
@click.option(
    "--answer-wordlist-path",
    "-a",
    type=str,
    default="3b1b-data/possible_words.txt",
    help="path to a text file where each valid answer word is on its own line",
)
def main(guess_wordlist_path, answer_wordlist_path):
    click.echo(f"Loading guess word list from {guess_wordlist_path}...")
    guess_wordlist = _read_words_from_file(guess_wordlist_path)
    guess_list_searcher = WordListSearcher()
    num_guess_words = guess_list_searcher.load_words(guess_wordlist)
    click.echo(f"Done! loaded {num_guess_words} guess words")

    click.echo(f"Loading answer word list from {answer_wordlist_path}...")
    answer_wordlist = _read_words_from_file(answer_wordlist_path)
    answer_list_searcher = WordListSearcher()
    num_answer_words = answer_list_searcher.load_words(answer_wordlist)
    click.echo(f"Done! loaded {num_answer_words} answer words")

    word_patterns_map = generate_similar_word_answer_sets(answer_wordlist)
    word_patterns_sorted = sorted(
        [(pattern, len(word_patterns_map[pattern])) for pattern in word_patterns_map],
        key=lambda kv: kv[1],
        reverse=True,
    )
    click.echo(f"20 of the largest word patterns:")
    for word_pattern, set_size in word_patterns_sorted[:20]:
        click.echo(f"{word_pattern} -> {word_patterns_map[word_pattern]}")

    # are there any combinations of 3 different letters that aren't covered by a valid guess word?
    letter_combos_map = {}
    for guess_word in guess_wordlist:
        for guess_letter_combo in itertools.combinations(guess_word, 3):
            if guess_letter_combo not in letter_combos_map:
                letter_combos_map[guess_letter_combo] = []
            letter_combos_map[guess_letter_combo].append(guess_word)
    click.echo(f"No valid guess words cover the following 3-letter combinations:")
    uncovered_combos = [
        "".join(letter_combo)
        for letter_combo in itertools.combinations(ALPHABET, 3)
        if letter_combo not in letter_combos_map
    ]
    click.echo(", ".join(uncovered_combos))
    for letter_combo in itertools.combinations(ALPHABET, 3):
        if (
            letter_combo in letter_combos_map
            and len(letter_combos_map[letter_combo]) < 3
        ):
            click.echo(
                f"Only {len(letter_combos_map[letter_combo])} guess words cover the letters {set(letter_combo)}: {letter_combos_map[letter_combo]}"
            )


if __name__ == "__main__":
    main()