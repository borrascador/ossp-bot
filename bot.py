import tweepy
import sys
import time
import os
from markov import Markov
from secret import *


auth = tweepy.OAuthHandler(KEY, KEY_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)
api = tweepy.API(auth)

minutes_interval = int(sys.argv[1])

dir = os.path.dirname(__file__)
filename = os.path.join(dir,
                        'fb-scraper',
                        '1500321840185061_facebook_statuses.csv'
                        )
markov = Markov(filename, seed=['but', 'except', ':'])
t = 0

while True:
    line = markov.generate_markov_text()
    while len(line) > 140:
        line = markov.generate_markov_text()
    api.update_status(line)
    t += 1
    print("Tweet #" + str(t) + " @ " + str(time.ctime()) + ":\n" + line)
    time.sleep(60 * minutes_interval)  # Tweet every x minutes