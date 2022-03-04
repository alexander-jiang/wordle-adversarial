## TODO
- [ ] implement a wordlist searcher that builds a trie and then brute forces all possible resolutions of yellow letters -> green letters. e.g. if first guess is "bread" with clues RRYGR, then the word must be either E__A_, _E_A_, or ___AE (the trie will visit all children if the letter is not specified)
- [x] more clever guess suggestions: returns valid guesses that do not use any of the grayed out letters
- [x] additional feature: only include valid guesses which use yellow letters, but not in the marked-yellow positions,
    - [ ] but maybe we should include guesses which don't use the yellow letters at all
    - [ ] don't include guesses which use yellow letters in positions that already have a green letter
- [x] a brute-force solver which tries all guess words and looks for forcing guesses (i.e. guess words such that every possibility is uniquely determined by the returned clues from the guess)
    - [x] optimization: only run this brute-force method when there are fewer than X answer words remaining (started with X = 10, then increased to X = 100)
    - [ ] optimization: only consider potential forcing guess candidates (must use at least one of the ambiguous letters i.e. must provide some additional info to narrow down the possible answer words)
- [ ] performance analysis: is the clue resolver the bottle-neck? Or should we prune how many guess words are tried?


- "ambiguous" letters: of all possible answer words (based on the clues), which letters appear in at least one of the possible answer words, but not in all possible answer words? These letters are "ambiguous" - if you guess a word with an ambiguous letter, you will be sure to narrow down the list of possible answer words (either by eliminating the answer words that use the letter if the letter is marked as gray, or by eliminating the answer words that don't use the letter if the letter is marked as yellow or green). I call this type of guess a "narrowing" guess: you're narrowing down the list of possible answer words by eliminating or confirming certain letters.
    - but often there are many "ambiguous" letters, especially early in the game when the list of possible answer words is very large. How to prioritize which ambiguous letters are most important to use in a narrowing guess?
    - ideally, your narrowing guess would be a word such that, in every possible outcome of what the revealed colors are, there is only one possible answer word remaining after accounting for that new information. This is a "forcing" guess: if the guessing player makes a "forcing" guess, then their next guess is guaranteed to be a "winning" guess (i.e. guessing the secret word)
    - but if this isn't possible, what then? intuitively, you'd pick a guess such that in the worst possible i.e. adversarial case, you have the fewest possible answer words left.

    But is it possible that having 5 answer words left (if there are many ambiguous letters remaining and it is difficult to fit them into a single word) is worse than having 6 or more answer words left (if there aren't as many ambiguous letters remaining, or the ambiguous letters can be easily grouped into a guessing word that narrows down the options)?

    The example below shows 5 answer words left, with 5 ambiguous letters (all consonants). Since there are no guess words that use 4 of the 5 ambiguous letters, the guessing player can guarantee a win in 3 more turns vs. an adversarial opponent.
    But consider an example where there are 6 answer words left, with 6 ambiguous letters, such that 5 of these 6 ambiguous letters can be placed into a single valid guess word. In such a situation, the guessing player could guarantee a win in just 2 turns vs. an adversarial opponent.

    Is the latter case actually possible?

example:
guess 1: sloth -> grrry
guess 2: share -> gggrg
    [At this point, there are only 5 possible answer words remaining: shade, shake, shame, shape, shave. This means there are 5 ambiguous letters, each with a frequency of 1: D, K, M, P, V. The ideal narrowing guess would be a hypothetical word that included 4 of these 5 ambiguous letters. If such a word existed, it would be a forcing guess: even if none of the 4 ambiguous letters in that word were marked as yellow or green, that would only indicate that the 5th ambiguous letter is the correct one to pick. However, there are no such valid guess words: the best you can do is to guess a word that uses 3 of the 5 ambiguous letters: amped, damps, dampy, dempt, dimps, dumka, dumky, dumps, dumpy, imped, kemps, kempt, kempy, meved, miked, mikva, moped, moved, padma, paved, pavid, piked, poked, puked, skimp, umped, vamps, vampy, vaped, vapid, vodka.]
guess 3: dumpy -> rrrrr
    [Now, there are 2 ambiguous letters corresponding to the two possible answer words remaining: shaKe and shaVe. In this case, there are many words that use both ambiguous letters or only one (any of which would be a forcing guess). Note that in these types of situations, when playing a non-adversarial game, the guessing player should just take the 50/50 chance by guessing one of the two remaining possible answer words. Doing so still is a forcing guess and there is no guess that guarantees a win on this turn, so guessing one of the 2 possible answers provides an additional 50% chance of winning on the first turn (which is not possible if you play a different forcing guess e.g. one that uses both ambiguous letters). I'll call this type of guess "free-rolling": in the non-adversarial case, it is best to have some non-zero chance of winning "early" by luck, while not sacrificing the guaranteed win in 2 turns (or whatever the best possible outcome is). But in the adversarial case, the adversary will never let you win "early", so you will have to settle for winning in 2 turns.]
guess 4: shake -> ggggg
    [Here, the free-rolling guess paid off. But in the adversarial case, the guessing player would have required one more guess to win.]

## Dev Env setup
```bash
# first time setup only (on Mac/linux)
$ python3 -m venv wordle-venv
# or first-time setup on windows
c:\>python -m venv wordle-venv

$ source wordle-venv/bin/activate
$ pip install -r requirements.txt

$ python -m wordle.cli.helper
$ python -m wordle.word_set_partitioner
# etc.
```

### Testing
```bash
$ pytest -rP
```

### Running the CLI helper
todo: include example command and input/output