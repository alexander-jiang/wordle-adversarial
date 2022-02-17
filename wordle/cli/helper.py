"""
CLI tool to run a Wordle "helper" program: you input the clue state
(i.e. word you tried, and which letters were colored gray, yellow, or green)
and it returns a list of possible answer words from the list

todo: maybe also returns valid guesses that do not use any of the grayed out letters
(additional feature: only include valid guesses which use yellow letters, but not in the 
marked-yellow positions, or in positions that already have a green letter)
"""
import click
from typing import List

from wordle.constants import WORDLE_COLUMNS
from wordle.word_list_searcher import WordListSearcher
from wordle.wordle_clues import WordleClues, WordleLetterState


def _read_words_from_file(wordlist_path: str) -> List[str]:
    wordlist = []
    with open(wordlist_path, "r") as wordlist_file:
        for word in wordlist_file.readlines():
            word_lower = word.lower().strip()
            if not _is_valid_guess(word_lower):
                print(f"Found an invalid word: {word_lower}")
            wordlist.append(word_lower)
    return wordlist


def _is_valid_guess(user_input: str) -> bool:
    """ validate the string has the right length and uses valid chars [a-zA-Z] """
    return len(user_input) == WORDLE_COLUMNS and user_input.isalpha()


def _is_valid_clues(user_input: str) -> bool:
    """ validate the string has the right length and uses valid chars [RrYyGg] """
    if len(user_input) != WORDLE_COLUMNS:
        return False
    for idx in range(len(user_input)):
        if user_input[idx].lower() not in ("r", "y", "g"):
            return False
    return True


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

    total_clues = WordleClues()
    next_guess = True
    total_guess_wordlist = set(guess_wordlist + answer_wordlist)
    possible_answers = set(answer_wordlist)
    while next_guess:
        next_guess = False

        guess_prompt = "Please enter your guess\n"
        guess = click.prompt(guess_prompt, type=str)
        while not _is_valid_guess(guess) or guess not in total_guess_wordlist:
            if not _is_valid_guess(guess):
                click.echo('Your guess was not correctly formatted, please try again')
            if guess not in total_guess_wordlist:
                click.echo('Your guess was not in the word list, please try again')
            guess = click.prompt(guess_prompt, type=str)
        guess = guess.lower()

        clues_prompt = (
            "Please enter the colors/clues (use R for gRay, Y for Yellow, G for Green)\n"
        )
        clues = click.prompt(clues_prompt, type=str)
        while not _is_valid_clues(clues):
            click.echo('Your clues string was not correctly formatted, please try again')
            clues = click.prompt(clues_prompt, type=str)
        clues = clues.lower()

        for idx in range(WORDLE_COLUMNS):
            if clues[idx] == "r":
                color = WordleLetterState.GRAY
            elif clues[idx] == "y":
                color = WordleLetterState.YELLOW
            elif clues[idx] == "g":
                color = WordleLetterState.GREEN
            else:
                raise Exception("should not get here: user input for clues is invalid")
            total_clues.mark(guess[idx], color, idx)

        matching_guess_words = guess_list_searcher.match(total_clues)
        print(f"Found {len(matching_guess_words)} matching guess words!")
        guesses_sample = matching_guess_words[:10]
        print(f"some guesses that align with the clues so far: {guesses_sample}")

        matching_answer_words = answer_list_searcher.match(total_clues)
        print(f"Found {len(matching_answer_words)} matching answer words!")
        answers_sample = matching_answer_words[:10]
        print(f"some potential answers: {answers_sample}")
        possible_answers = set(matching_answer_words)

        if len(possible_answers) == 1:
            click.echo(f'There is only one possible answer word left: {list(possible_answers)[0]}')
            break
        elif len(possible_answers) == 0:
            click.echo(f'There are no possible answer words left, something went wrong...')
            break

        next_guess = click.confirm("Do you want to continue?")
        

    click.echo("Goodbye!")


if __name__ == "__main__":
    main()