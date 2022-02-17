"""
CLI tool to run a Wordle "helper" program: you input the clue state
(i.e. word you tried, and which letters were colored gray, yellow, or green)
and it returns a list of possible answer words from the list

todo: maybe also returns valid guesses that do not use any of the grayed out letters
(additional feature: only include valid guesses which use yellow letters, but not in the 
marked-yellow positions, or in positions that already have a green letter)
"""
import click

from word_list_searcher import WordListSearcher

@click.command()
@click.option('--guess-wordlist-path', '-g', type=str, default='3b1b-data/allowed_words.txt'
              help='path to a text file where each valid guess word is on its own line')
@click.option('--answer-wordlist-path', '-a', type=str, default='3b1b-data/possible_words.txt'
              help='path to a text file where each valid answer word is on its own line')
def main(guess_wordlist_path, answer_wordlist_path):
    click.echo(f'loading guess word list from {guess_wordlist_path}...')
    with open(guess_wordlist_path, 'r') as guess_wordlist_file:
        guess_wordlist = guess_wordlist_file
    guess_list_searcher = WordListSearcher()
    num_guess_words = guess_list_searcher.load_words(guess_wordlist)
    click.echo(f'done! loaded {num_guess_words} guess words')

    click.echo(f'loading answer word list from {answer_wordlist_path}...')
    answer_list_searcher = WordListSearcher()
    num_answer_words = answer_list_searcher.load_words(answer_word_list)
    click.echo(f'done! loaded {num_num_answer_wordsguess_words} guess words')

    continue = True
    while continue:
        continue = False
        guess = click.prompt('Please enter your guess', type=str)
        clues = click.prompt('Please enter the colors/clues (use R for gRay, Y for Yellow, G for Green)', type=str)
        continue = click.confirm('Do you want to continue?')


if __name__ == "__main__":
    main()