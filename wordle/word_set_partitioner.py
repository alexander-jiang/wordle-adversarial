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


def generate_4gram_answer_sets(answer_wordlist: List[str]):
    word_patterns: Dict[str, List[str]] = {}
    for answer_word in answer_wordlist:
        for idx in range(WORDLE_COLUMNS):
            word_pattern_key = answer_word[:idx] + "_" + answer_word[idx + 1 :]
            if word_pattern_key not in word_patterns:
                word_patterns[word_pattern_key] = []
            word_patterns[word_pattern_key].append(answer_word)
    return word_patterns

def generate_3gram_answer_sets(answer_wordlist: List[str]):
    word_patterns: Dict[str, List[str]] = {}
    for answer_word in answer_wordlist:
        for indexes in itertools.combinations(range(WORDLE_COLUMNS), 3):
            word_pattern_key = ""
            for idx in range(WORDLE_COLUMNS):
                if idx in indexes:
                    word_pattern_key += answer_word[idx]
                else:
                    word_pattern_key += "_"
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

    # are there any combinations of 3 different letters that aren't covered by a valid guess word?
    letter_combos_map = {}
    for guess_word in guess_wordlist:
        for guess_letter_combo in itertools.combinations("".join(set(guess_word)), 3):
            guess_letter_combo = tuple(sorted(guess_letter_combo))
            if guess_letter_combo not in letter_combos_map:
                letter_combos_map[guess_letter_combo] = []
            # dedupe the combos from words with doubled/multiple letters
            if guess_word not in letter_combos_map[guess_letter_combo]:
                letter_combos_map[guess_letter_combo].append(guess_word)

    # click.echo(f'how many keys in the letter_combos_map (should be <= 2600 i.e. 26 choose 3): {len(letter_combos_map.keys())}')
    uncovered_combos = [
        "".join(sorted(letter_combo))
        for letter_combo in itertools.combinations(ALPHABET, 3)
        if letter_combo not in letter_combos_map
    ]
    click.echo(
        f"No valid guess words cover the following {len(uncovered_combos)} (of 2600) three-letter combinations:"
    )
    click.echo(", ".join(uncovered_combos))
    # count = 0
    # for letter_combo in itertools.combinations(ALPHABET, 3):
    #     if (
    #         letter_combo in letter_combos_map
    #         and len(letter_combos_map[letter_combo]) == 1
    #     ):
    #         count += 1
    #         click.echo(
    #             f"Only {len(letter_combos_map[letter_combo])} guess word covers the letters {letter_combo}: {letter_combos_map[letter_combo]}"
    #         )
    # click.echo(
    #     f"total of {count} 3-letter combos that are covered by only 1 guess word each"
    # )

    # distribution of freq of letter combos among guess words (i.e. how many 3-letter combos are such that exactly N guess words cover that letter combo?)
    # maps the count of how many guess words cover it to the combo
    count_distribution = {0: len(uncovered_combos)}
    for letter_combo in letter_combos_map:
        combo_freq = len(letter_combos_map[letter_combo])
        if combo_freq not in count_distribution:
            count_distribution[combo_freq] = 0
        count_distribution[combo_freq] += 1
    # click.echo(
    #     f"distribution of counts (of the number of guess words that cover 3-letter combos):"
    # )
    # click.echo(count_distribution)

    bucketed_count_distribution = {}
    for count in range(11):
        bucketed_count_distribution[str(count)] = count_distribution[count]
    # bucketed_count_distribution['6-10'] = sum([count_distribution[count] for count in count_distribution if 6 <= count <= 10])
    bucketed_count_distribution["11-50"] = sum(
        [count_distribution[count] for count in count_distribution if 11 <= count <= 50]
    )
    bucketed_count_distribution["51-100"] = sum(
        [
            count_distribution[count]
            for count in count_distribution
            if 51 <= count <= 100
        ]
    )
    bucketed_count_distribution[">100"] = sum(
        [count_distribution[count] for count in count_distribution if count > 100]
    )
    click.echo(
        f"bucketed distribution of counts (of the number of guess words that cover 3-letter combos):"
    )
    click.echo(bucketed_count_distribution)

    # are there any sets of 4+ answer words that only differ in one position?
    # note that we need 4 different letters: i'm assuming any pair of different letters is covered by at least one 
    # guess word. And if there are only 3 different letters, then you just need a guess that covers any two of them
    # to guarantee a win on the following guess.
    word_patterns_map = generate_4gram_answer_sets(answer_wordlist)
    word_patterns_sorted = sorted(
        [(pattern, len(word_patterns_map[pattern])) for pattern in word_patterns_map],
        key=lambda kv: kv[1],
        reverse=True,
    )

    word_patterns_at_least_4 = {pattern: word_patterns_map[pattern] for pattern in word_patterns_map if len(word_patterns_map[pattern]) >= 4}
    click.echo(f"all word patterns with 4+ different letters:")
    for word_pattern in word_patterns_at_least_4:
        different_idx = word_pattern.index("_")
        full_matching_words = word_patterns_at_least_4[word_pattern]
        different_letters_only = [word[different_idx] for word in full_matching_words]
        word_patterns_at_least_4[word_pattern] = different_letters_only
        click.echo(f"{word_pattern} -> {word_patterns_at_least_4[word_pattern]}")

    # For word patterns with 4 different letters, are there any valid guess words that can cover at least 3 of the different letters?
    click.echo(f'for word patterns with exactly 4 different letters, are there any valid guess words that cover at least 3 of them?')
    for word_pattern, letters in word_patterns_at_least_4.items():
        if len(letters) != 4:
            continue
        can_cover = False
        covering_combo = None
        for letter_combo in itertools.combinations(letters, 3):
            if "".join(sorted(letter_combo)) not in uncovered_combos:
                can_cover = True
                covering_combo = "".join(sorted(letter_combo))
                break
        if can_cover:
            guess_letter_combo = tuple(sorted(covering_combo))
            click.echo(f"{word_pattern} -> {word_patterns_at_least_4[word_pattern]} -> covered by {covering_combo} e.g. {letter_combos_map[guess_letter_combo][0]}")
        else:
            click.echo(f"{word_pattern} -> {word_patterns_at_least_4[word_pattern]} -> no 3 letters are coverable by a valid guess!")

    click.echo(f'for word patterns with N>4 different letters, are there any valid guess words that cover at least N-1 of them?')
    for word_pattern, _ in word_patterns_sorted:
        letters = word_patterns_map[word_pattern]
        if len(letters) <= 4:
            continue
        can_cover = False
        covering_combo = None
        covering_word = None
        for letter_combo in itertools.combinations(letters, len(letters) - 1):
            for guess_word in guess_wordlist:
                if all([(letter in guess_word) for letter in letter_combo]):
                    can_cover = True
                    covering_combo = "".join(sorted(letter_combo))
                    covering_word = guess_word
                    break
        if can_cover:
            guess_letter_combo = tuple(sorted(covering_combo))
            click.echo(f"{word_pattern} -> {word_patterns_at_least_4[word_pattern]} -> covered by {covering_combo} e.g. {covering_word}")
        else:
            click.echo(f"{word_pattern} -> {word_patterns_at_least_4[word_pattern]} -> no {len(letters) - 1} letters are coverable by a valid guess!")

    # are there any sets of answer words that only differ in two positions?
    word_3gram_patterns_map = generate_3gram_answer_sets(answer_wordlist)
    word_3gram_patterns_sorted = sorted(
        [(pattern, len(word_3gram_patterns_map[pattern])) for pattern in word_3gram_patterns_map],
        key=lambda kv: kv[1],
        reverse=True,
    )
    click.echo(f"word patterns with 3 shared letters:")
    for pattern, _ in word_3gram_patterns_sorted[:10]:
        click.echo(f"{pattern} -> {word_3gram_patterns_map[pattern]}")
    


if __name__ == "__main__":
    main()