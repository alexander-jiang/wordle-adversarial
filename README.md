## TODO
- implement a wordlist searcher that builds a trie and then brute forces all possible resolutions of yellow letters -> green letters. e.g. if first guess is "bread" with clues RRYGR, then the word must be either E__A_, _E_A_, or ___AE (the trie will visit all children if the letter is not specified)

## Dev Env setup
```bash
# first time setup only (on Mac/linux)
$ python3 -m venv wordle-venv
# or first-time setup on windows
c:\>python -m venv wordle-venv

$ source wordle-venv/bin/activate
$ pip install -r requirements.txt
```

### Testing
```bash
$ pytest -rP
```

### Running the CLI helper
todo: include example command and input/output