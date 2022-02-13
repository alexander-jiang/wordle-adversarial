"""
CLI tool to run a Wordle "helper" program: you input the clue state
(i.e. word you tried, and which letters were colored gray, yellow, or green)
and it returns a list of possible answer words from the list

todo: maybe also returns valid guesses that do not use any of the grayed out letters
(additional feature: only include valid guesses which use yellow letters, but not in the 
marked-yellow positions, or in positions that already have a green letter)
"""