import time
import sys
from markov import Markov


start_time = time.time()

seed_word = str(sys.argv[1])
iterations = int(sys.argv[2])

markov = Markov('ossp-posts.csv')

for i in range(iterations):
    line = markov.generate_markov_text(seed_word=seed_word)
    if len(line) > 140:
        line = line[:140]
    print(line, "\n")

print("--- %s seconds ---" % (time.time() - start_time))
