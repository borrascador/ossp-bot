import csv, random, tweepy, time



class Markov(object):

    def __init__(self, open_csv):
        self.cache = {}
        self.open_csv = open_csv
        self.words = self.csv_to_words()
        self.word_size = len(self.words)
        self.database()
    
    def csv_to_words(self):
        posts = []  
        with open(self.open_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                posts.append(row[1])
        f.close()
        
        for p, s in enumerate(posts):
            posts[p] = s[2:-1]
            
            if posts[p] == '' or posts[p][-1] in ['.','!']:
                continue
            else:
                posts[p] = posts[p]+'.'
               
        words = [word for post in [post.split() for post in posts] for word in post]
        
        return words
    
    def triples(self):
        '''
            Generates triples from the given data string. So if our string were
            "What a lovely day", we'd generate (What, a, lovely) and then
            (a, lovely, day).
        '''
        
        if len(self.words) < 3:
            return
        
        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i+1], self.words[i+2])
    
    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]
    
    def generate_markov_text(self, seed_word=None, size=25):
        if (seed_word in self.words) and (seed_word != None):
            matches = [i for i, j in enumerate(self.words) if j == seed_word]
            seed = random.choice(matches)
        else:
            seed = random.randint(0, self.word_size-3)
        
        seed_word, next_word = self.words[seed], self.words[seed+1]
        
        w1, w2 = seed_word, next_word
        gen_words = []
        for i in range(size):
            gen_words.append(w1)
            if w1[-1] in ['.', '!']: return ' '.join(gen_words)
            w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w2)
        return ' '.join(gen_words)

CONSUMER_KEY = 'H9EifLJVaNUb86WPtstBP2GdZ'
CONSUMER_SECRET = 'Ev8JwCYX8gQgjcSLQlmG8XqA0HCVUHxeZfsNngZpwMoZ3wab1C'
ACCESS_KEY = '832633493427326976-3sbvHxfsoCR0qhLACIECOBOjZ5guHdM'
ACCESS_SECRET = 'fOFQXlk7pzn7zzUk7WxOGLS5lT2SvBPtSFE9SwAv0G9Az'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

markov = Markov('ossp-posts.csv')

while True:
    line = markov.generate_markov_text()
    if len(line)>140: line = line[:140]
    api.update_status(line)
    time.sleep(300) #Tweet every 5 minutes
