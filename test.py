import sys
from markov import Markov

seed_word = str(sys.argv[1])
iterations = int(sys.argv[2])

for i in range(iterations):
    markov = Markov('ossp-posts.csv')
    line = markov.generate_markov_text(seed_word=seed_word)
    if len(line) > 140:
        line = line[:140]
    print(line)
