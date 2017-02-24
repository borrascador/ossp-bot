import time
import sys
from markov import Markov


start_time = time.time()

seed_word = str(sys.argv[1])
depth = int(sys.argv[2])
iterations = int(sys.argv[3])

markov = Markov('fb-scraper/1500321840185061_facebook_statuses.csv',
                depth=depth
                )

for i in range(iterations):
    line = markov.generate_markov_text(seed_word=seed_word)
    while len(line) > 140:
        line = markov.generate_markov_text(seed_word=seed_word)
    print("\n" + line)

print("\n--- %s seconds ---" % (time.time() - start_time))
