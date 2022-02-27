"""
CLI tool to run a Wordle "helper" program: you input the clue state
(i.e. word you tried, and which letters were colored gray, yellow, or green)
and it returns a list of possible answer words from the list
"""
import click
from typing import List, Tuple

from wordle.clue_resolver import _reveal_clues
from wordle.constants import WORDLE_COLUMNS
from wordle.word_list_searcher import (
    WordListSearcher,
    _read_words_from_file,
    _is_valid_guess,
    _is_valid_clues,
)
from wordle.wordle_clues import WordleClues, WordleLetterState
from wordle.word_set_partitioner import partition, pick_narrowing_guesses_by_letters


def _print_state_with_colors(state: List[Tuple[str, str]]) -> None:
    for guess, clues in state:
        output_str = ""
        for idx in range(WORDLE_COLUMNS):
            if clues[idx] == "r":
                output_str += f"\033[30;100m{guess[idx]}\033[0m"
            elif clues[idx] == "y":
                output_str += f"\033[30;103m{guess[idx]}\033[0m"
            elif clues[idx] == "g":
                output_str += f"\033[30;102m{guess[idx]}\033[0m"
        print(output_str)


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

    actual_clues = WordleClues()
    helpful_guess_clues = WordleClues()
    total_guess_wordlist = set(guess_wordlist)
    possible_answers = set(answer_wordlist)
    gray_letters = set()
    yellow_letters = set()
    green_letters = set()
    state = []
    while True:
        guess_prompt = "Your guess\n"
        guess = click.prompt(guess_prompt, type=str)
        while not _is_valid_guess(guess) or guess not in total_guess_wordlist:
            if not _is_valid_guess(guess):
                click.echo("Your guess was not valid, please try again")
            if guess not in total_guess_wordlist:
                click.echo("Your guess was not in the word list, please try again")
            guess = click.prompt(guess_prompt, type=str)
        guess = guess.lower()

        clues_prompt = (
            "The revealed colors (use R for gRay, Y for Yellow, G for Green)\n"
        )
        clues = click.prompt(clues_prompt, type=str)
        while not _is_valid_clues(clues):
            click.echo("Your colors were not valid, please try again")
            clues = click.prompt(clues_prompt, type=str)
        clues = clues.lower()
        state.append((guess, clues))
        _print_state_with_colors(state)

        for idx in range(WORDLE_COLUMNS):
            if clues[idx] == "r":
                color = WordleLetterState.GRAY
                gray_letters.add(guess[idx])
            elif clues[idx] == "y":
                color = WordleLetterState.YELLOW
                yellow_letters.add(guess[idx])
            elif clues[idx] == "g":
                color = WordleLetterState.GREEN
                green_letters.add(guess[idx])
            else:
                raise Exception("should not get here: user input for clues is invalid")

            actual_clues.mark(guess[idx], color, idx)
            # for 'helpful' guesses: don't include guess words that use the gray letters or that use yellow letters in wrong positions
            if color == WordleLetterState.GRAY or color == WordleLetterState.YELLOW:
                helpful_guess_clues.mark(guess[idx], color, idx)

        # helpful_guesses = guess_list_searcher.match(helpful_guess_clues)
        # print(
        #     f"{len(helpful_guesses)} 'helpful' guesses (i.e. don't use the gray letters {gray_letters} or yellow letters in yellow positions):"
        # )
        # print(", ".join(sorted(helpful_guesses)))

        matching_answer_words = answer_list_searcher.match(actual_clues)
        print(f"Found {len(matching_answer_words)} matching answer words:")
        print(", ".join(sorted(matching_answer_words)))
        possible_answers = set(matching_answer_words)

        # ambiguous_letters = partition(possible_answers)
        # searching_guesses, num_used_letters = pick_narrowing_guesses_by_letters(
        #     ambiguous_letters, guess_wordlist
        # )
        # if len(ambiguous_letters) > 0:
        #     click.echo(
        #         f'"searching" guesses (i.e. use maximal {num_used_letters} of {len(ambiguous_letters)} ambiguous letters from matching answer words:)'
        #     )
        #     click.echo(", ".join(searching_guesses))

        # look for forcing guesses: guesses such that, no matter what the returned clues are, there is only
        # one possible answer word remaining (i.e. a forcing guess guarantees a win on the next guess)
        if len(possible_answers) > 2 and len(possible_answers) <= 243:
            # if there are only 2 possible answer words left, guessing either of them is a forcing guess
            # And note that that if there are more than 3^5 = 243 possible answers, by pigeonhole principle, there
            # is a clue string that is returned by at least two of the possible answer words.
            click.echo("Searching for forcing guesses...")
            forcing_guess_words = []
            for guess_candidate in guess_wordlist:
                clues_to_answers = {}
                is_forcing_guess = True
                for possible_answer in possible_answers:
                    clues = _reveal_clues(guess_candidate, possible_answer)
                    if clues in clues_to_answers:
                        is_forcing_guess = False
                        break
                    else:
                        clues_to_answers[clues] = set([guess_candidate,])
                if is_forcing_guess:
                    forcing_guess_words.append(guess_candidate)
            if len(forcing_guess_words) > 0:
                answer_guesses = [word for word in forcing_guess_words if word in possible_answers]
                if len(answer_guesses) > 0:
                    click.echo(f"Found forcing guesses that are also possible answers: {answer_guesses}")
                    click.echo(f"There are {len(forcing_guess_words)} total forcing guesses")
                else:
                    click.echo(f"Found {len(forcing_guess_words)} total forcing guesses: {forcing_guess_words}")
            else:
                click.echo("No forcing guesses found")
        elif len(possible_answers) == 1:
            click.echo(
                f"There is only one possible answer word left: {list(possible_answers)[0]}"
            )
            break
        elif len(possible_answers) == 0:
            click.echo(
                f"There are no possible answer words left, something went wrong..."
            )
            break

    click.echo("Goodbye!")


if __name__ == "__main__":
    main()