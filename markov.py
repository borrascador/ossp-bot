import csv, random
from unicodetoascii import unicodetoascii



class Markov(object):

    def __init__(self, open_csv):
        self.depth = 3
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
        
        posts = [post.split() for post in posts]
        words = [unicodetoascii(word) for post in posts \
        for word in post]

        return words
    
    def tuples(self):
        '''
            Generates tuples from the given data string and the 
            chosen markov chain length, called depth. So if our
            string were "What a lovely day" with depth 3, we'd 
            generate (What, a, lovely) and then 
            (a, lovely, day).
        '''
        
        if len(self.words) < self.depth:
            return
        
        for i in range(len(self.words) - (self.depth - 1)):
            yield tuple(self.words[i+j] for j in range(self.depth))
    
    def database(self):
        for tuple in self.tuples():
            key = tuple[:-1]
            if key in self.cache:
                self.cache[key].append(tuple[-1])
            else:
                self.cache[key] = [tuple[-1]]
    
    def generate_markov_text(self, seed_word=None, size=25):
        if (seed_word in self.words) and (seed_word != None):
            matches = [i for i, j in enumerate(self.words) \
            if j == seed_word]
            seed = random.choice(matches)
        else:
            seed = random.randint(0, self.word_size-self.depth)
        
        seed_words = [self.words[seed+i] for i in range(self.depth)]
        
        gen_words = []
        
        for i in range(size):
            gen_words.append(seed_words[0])
            if seed_words[0][-1] in ['.', '!']: 
                return ' '.join(gen_words)
            del seed_words[0]
            key = tuple(seed_words)
            seed_words.append(random.choice(self.cache[key]))
            
        gen_words.append(seed_words[-1])
        return ' '.join(gen_words)
        
