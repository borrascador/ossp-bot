import tweepy
import time
from markov import Markov
from secret import *


auth = tweepy.OAuthHandler(KEY, KEY_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)
api = tweepy.API(auth)

markov = Markov('ossp-posts.csv')
t = 0

while True:
    line = markov.generate_markov_text('but')
    if len(line) > 140:
        line = line[:140]
    api.update_status(line)
    t += 1
    print("Tweet #" + str(t) + " @ " + str(time.ctime()) + ":\n" + line)
    time.sleep(600)  # Tweet every 10 minutes
