import tweepy, time
from markov import Markov
from passwords import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, \
ACCESS_SECRET

KEY = CONSUMER_KEY
KEY_SECRET = CONSUMER_SECRET
TOKEN = ACCESS_KEY
TOKEN_SECRET = ACCESS_SECRET

auth = tweepy.OAuthHandler(KEY, KEY_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)
api = tweepy.API(auth)

markov = Markov('ossp-posts.csv')

while True:
    line = markov.generate_markov_text()
    if len(line)>140: line = line[:140]
    api.update_status(line)
    time.sleep(1200) #Tweet every 5 minutes
