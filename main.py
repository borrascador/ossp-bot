import tweepy
import time
import os
from markov import Markov
from secret import *

directory = os.path.dirname(__file__)
filename = os.path.join(directory,
                        'fb-scraper',
                        '1500321840185061_facebook_statuses.csv'
                        )
markov = Markov(filename, seed=['but', 'except', ':'])

line = markov.generate_markov_text()
while len(line) > 140:
    line = markov.generate_markov_text()

auth = tweepy.OAuthHandler(KEY, KEY_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)
api = tweepy.API(auth)
api.update_status(line)

print("@{} tweeted @ {}:\n{}".format(api.me().screen_name, time.ctime(),line))

