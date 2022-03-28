"""
Given a set of possible answer words, what is the best way to
partition the words? based on things like letter frequency, letter combos,
letter-position frequency, etc.
"""
import click
import itertools
from typing import List, Dict, MutableSet, Tuple, Optional

from wordle.word_list_searcher import WordListSearcher, _read_words_from_file
from wordle.constants import WORDLE_COLUMNS, ALPHABET


def partition(words: List[str], print_debug: bool = True) -> List[str]:
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

    if print_debug and len(words) > 1:
        print(f"of {len(words)} words, these are ambiguous letter frequencies:")
        letter_freq_kvs = [
            (letter, letter_freqs[letter])
            for letter in letter_freqs
            if letter_freqs[letter] != 0 and letter_freqs[letter] != len(words)
        ]
        sorted_freq_kvs = sorted(letter_freq_kvs, key=lambda kv: kv[1], reverse=True)
        print(sorted_freq_kvs)

    return differentiating_letters


# of any two possible answer words, a forcing guess must be able to differentiate them: build a set of letters such that
# a forcing guess must contain at least one of the returned letters
# Note: just checking letters is too strict: what if two words share the same letters but in different positions? then a guess could
# differentiate between them if it checked the letters in specific positions
def required_letter_positions_for_forcing_guess(answer_words: List[str], print_debug: bool = True) -> Dict[Tuple[str, str], Tuple[MutableSet[str], MutableSet[Tuple[int, str]]]]:
    required_letter_positions = {}
    for word1, word2 in itertools.combinations(answer_words, 2):
        ambiguous_letter_positions = set()
        ambiguous_letters = set()

        for i in range(len(word1)):
            letter1 = word1[i]
            letter2 = word2[i]
            if letter1 == letter2:
                continue # no way to distinguish

            # can always distinguish by guessing letter1 in this position or letter2 in this position
            ambiguous_letter_positions.update([(letter1, i), (letter2, i)])

            if letter1 not in word2:
                # can distinguish by guessing letter1 in any position
                ambiguous_letter_positions.update([(letter1, i) for i in range(len(word1))])
                ambiguous_letters.add(letter1)
            else:
                # if word2's occurrences of letter1 don't all match up with word1's occurrences of letter1, we
                # can distinguish by guessing letter1 at any index (where word1 and word2 don't both have letter1)
                covered = True
                for j in range(len(word2)):
                    if word2[j] == letter1 and word1[j] != letter1:
                        covered = False
                        break
                if covered:
                    for j in range(len(word2)):
                        if word2[j] != letter1 or word1[j] != letter1:
                            ambiguous_letter_positions.add((letter1, j))
                # otherwise, you can't distinguish by guessing letter1 (except at index i, which is already accounted for above)

            if letter2 not in word1:
                # can distinguish by guessing letter2 in any position
                ambiguous_letter_positions.update([(letter2, i) for i in range(len(word2))])
                ambiguous_letters.add(letter2)
            else:
                # if word1's occurrences of letter2 don't all match up with word2's occurrences of letter2, we
                # can distinguish by guessing letter2 at any index (where word2 and word1 don't both have letter2)
                covered = True
                for j in range(len(word1)):
                    if word1[j] == letter2 and word2[j] != letter2:
                        covered = False
                        break
                if covered:
                    for j in range(len(word1)):
                        if word1[j] != letter2 or word2[j] != letter2:
                            ambiguous_letter_positions.add((letter2, j))
                # otherwise, you can't distinguish by guessing letter2 (except at index i, which is already accounted for above)

        required_letter_positions[(word1, word2)] = ambiguous_letters, ambiguous_letter_positions

    return required_letter_positions

def _word_to_letter_pos_map(word: str) -> Dict[str, MutableSet[int]]:
    # TODO update this to return a matrix: rows = letters, columns = positions
    letter_pos_map = {}
    for idx in range(len(word)):
        letter = word[idx]
        if letter not in letter_pos_map:
            letter_pos_map[letter] = set()
        letter_pos_map[letter].add(idx)
    return letter_pos_map

# goal: given only a list of possible answer words, build a list of necessary conditions that
# a potential guess must fulfill to be possibly a forcing guess
def forcing_guess_requirements(answer_words: List[str], guess_letters: Optional[List[Optional[str]]] = None):
    # for each letter, which positions must it be in, in the guess word in order to even possibly
    # be a forcing guess?
    answer_letter_pos_maps = [_word_to_letter_pos_map(word) for word in answer_words]
    for letter in ALPHABET:
        pos_freq = [0 for _ in range(WORDLE_COLUMNS)]
        for letter_pos_map in answer_letter_pos_maps:
            if letter in letter_pos_map:
                for idx in letter_pos_map[letter]:
                    pos_freq[idx] += 1
        if not any(pos_freq):
            continue
            # letter doesn't appear in any of the possible answer words, so including this letter isn't necessary for a forcing guess
        print(f'letter {letter} appears in answer word positions with this frequency {pos_freq}')

    # if total of pos_freq is 0, then guessing the letter in any position isn't helpful (gains 0 "points")
    # if total of pos_freq is 1, then guessing the letter in any position helps
    #  by either confirming or eliminating the possible answer
    #  word that uses the letter in that position (gains 1 point = 1 word)
    # if total of pos_freq is >1, then guessing the letter in position X earns the minimum of
    #  (number of occurrences of the letter at position X) and (number of occurrences of the
    #  letter at all other positions besides X)
    #  -> because number of words that can be guaranteed eliminated or confirmed is the adversarial case:
    #     either the letter is in the true answer word at X (which eliminates all occurrences of the )
    # TODO what about letters that appear multiple times in an answer word?
    def scoring_func(guess_candidate: str) -> int:
        pass

"""
answer words: ether, other, their, three, threw

letter e appears in answer word positions with this frequency [1, 0, 1, 4, 1]
letter h appears in answer word positions with this frequency [0, 3, 2, 0, 0] -> {their, three, threw} vs. {ether, other}
letter i appears in answer word positions with this frequency [0, 0, 0, 1, 0] -> {their} vs. all others
letter o appears in answer word positions with this frequency [1, 0, 0, 0, 0] -> {other} vs. all others
letter r appears in answer word positions with this frequency [0, 0, 2, 0, 3] -> {three, threw} vs. {ether, other, their}
letter t appears in answer word positions with this frequency [3, 2, 0, 0, 0] -> {their, three, threw} vs. {ether, other}
letter w appears in answer word positions with this frequency [0, 0, 0, 0, 1] -> {threw} vs. all others

three dimensional matrix: letter, position, and answer word index
e.g. label the answer words with indexes: "ether" is 0, "other" is 1, etc.
guess candidate = 'ether' ->
matrix['e'][0]['ether'] = 1
matrix['t'][1]['ether'] = 1, matrix['t'][1]['other'] = 1
matrix['h'][2]['ether'] = 1, matrix['h'][2]['other'] = 1
matrix['e'][3]['ether'] = 1, matrix['e'][3]['other'] = 1, matrix['e'][3]['their'] = 0, matrix['e'][3]['three'] = 1, matrix['e'][3]['threw'] = 1
matrix['r'][4]['ether'] = 1, matrix['r'][4]['other'] = 1, matrix['r'][4]['their'] = 1, matrix['r'][4]['three'] = 0, matrix['r'][4]['threw'] = 0

then you compare: for each answer word, for each letter-pos in the guess candidate, and each string needs to be different
(the series of answers to each of the questions needs to be different for each answer word -> this leads to different clues)
matrix['e', 't', 'h', 'e', 'r'][0-4]['ether'] = 11111
matrix['e', 't', 'h', 'e', 'r'][0-4]['other'] = 01111
matrix['e', 't', 'h', 'e', 'r'][0-4]['their'] = 00001
matrix['e', 't', 'h', 'e', 'r'][0-4]['three'] = 00010 -> different from THREW as the first E in the guess ETHER will be yellow vs. gray
matrix['e', 't', 'h', 'e', 'r'][0-4]['threw'] = 00010

matrix['t', 'h', 'r', 'e', 'e'][0-4]['ether'] = 00010 -> different from OTHER as the second E in the guess THREE will be yellow vs. gray
matrix['t', 'h', 'r', 'e', 'e'][0-4]['other'] = 00010
matrix['t', 'h', 'r', 'e', 'e'][0-4]['their'] = 11000
matrix['t', 'h', 'r', 'e', 'e'][0-4]['three'] = 11111
matrix['t', 'h', 'r', 'e', 'e'][0-4]['threw'] = 11110

-> the key optimization? the matrix can be precomputed without knowing the guess candidate
-> one tricky edge case: when the guess candidate contains multiple of the same letter, then the rules around duplicate letters become tricky
"""


def can_partition_with_guess(answer_words: List[str], guess_letters: Optional[List[Optional[str]]] = None) -> bool:
    if guess_letters is None:
        guess_letters = [None for _ in range(WORDLE_COLUMNS)]

    print(f'partitioning answer words using guess_letters: {guess_letters}')
    print(answer_words)
    for position in range(WORDLE_COLUMNS):
        if guess_letters[position] is not None:
            continue # already have a letter in this position

        for letter in ALPHABET:
            # if guess contains letter at this position, how does that split the bucket of answer words
            # (based on the clue returned for this position)?
            new_guess_letters = guess_letters.copy()
            new_guess_letters[position] = letter
            print(f'trying letter {letter} in index {position}')

            # which answer words would remain if this clue was green/yellow/gray?
            green_clue_answer_words = []
            yellow_clue_answer_words = []
            gray_clue_answer_words = []
            for answer_word in answer_words:
                if answer_word[position] == letter:
                    green_clue_answer_words.append(answer_word)
                elif letter in answer_word:
                    yellow_clue_answer_words.append(answer_word)
                    # TODO this is tricky if the letter appears multiple times in the word
                else:
                    gray_clue_answer_words.append(answer_word)
            if (
                len(gray_clue_answer_words) == len(answer_words)
                or len(yellow_clue_answer_words) == len(answer_words)
                or len(green_clue_answer_words) == len(answer_words)
            ):
                continue # all words would return the same clue for this letter, try the next one

            able_to_partition = True
            if len(green_clue_answer_words) > 2:
                able_to_partition_green = can_partition_with_guess(green_clue_answer_words, new_guess_letters)
                able_to_partition = able_to_partition and able_to_partition_green
            if len(yellow_clue_answer_words) > 2:
                able_to_partition_yellow = can_partition_with_guess(yellow_clue_answer_words, new_guess_letters)
                able_to_partition = able_to_partition and able_to_partition_yellow
            if len(gray_clue_answer_words) > 2:
                able_to_partition_gray = can_partition_with_guess(gray_clue_answer_words, new_guess_letters)
                able_to_partition = able_to_partition and able_to_partition_gray
            if able_to_partition:
                return able_to_partition
    return False


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