import csv
import random
import re
from string import punctuation


class Markov(object):

    def __init__(self, open_csv, seed=None, depth=4):
        self.seed = seed
        self.depth = depth
        self.cache = {}
        self.open_csv = open_csv
        self.words = self.get_words()
        self.word_size = len(self.words)
        self.database()

    def get_words(self):
        words = []
        try:
            with open('words.txt', 'r', encoding='UTF-8') as f:
                words = f.readlines()
                words = [x.strip() for x in words]
            f.close()
            
        except IOError:
            posts = []
            with open(self.open_csv, 'r', encoding='UTF-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    posts.append(row[1])
            f.close()
            
            del posts[0]

            # Remove spaces before colons and semicolons
            pattern1 = re.compile(r'\s:|\s;')
            posts = [re.sub(pattern1, ':', s) for s in posts]
            
            # Remove double quotes and parentheses from all posts
            pattern2 = re.compile(r'\"|\(|\)')
            posts = [re.sub(pattern2, '', s) for s in posts]

            for p, s in enumerate(posts):
                posts[p] = s
                if (posts[p] == '') or (posts[p][-1] in ['.', '!', '?']):
                    continue
                
                else:
                    posts[p] = posts[p].strip()+'.'

            posts = [post.split() for post in posts]
            words = [word for post in posts for word in post]

            with open('words.txt', 'w', encoding='UTF-8') as f:
                for word in words:
                    f.write("{}\n".format(word))
            f.close()

        return words

    def tuples(self):
        '''
            Generates tuples from the given data string and the chosen
            markov chain length, called depth. So if our string were
            "What a lovely day" with depth 3, we'd generate (What, a,
            lovely) and then (a, lovely, day).
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

    def build_chain(self):
        if self.seed_word == ':':
            pattern = re.compile(r'[\w]+:')
            matches = [i for i, j in enumerate(self.words)
                       if re.match(pattern, j)]
            seed_num = random.choice(matches)
        elif (self.seed_word in self.words) and (self.seed_word is not None):
            matches = [i for i, j in enumerate(self.words) 
                       if j == self.seed_word]
            seed_num = random.choice(matches)
        else:
            seed_num = random.randint(0, self.word_size-self.depth)

        return [self.words[seed_num+i] for i in range(self.depth)]

    def generate_markov_text(self):
        if isinstance(self.seed, list):
            self.seed_word = random.choice(self.seed)
        else:
            self.seed_word = self.seed

        seed_chain = self.build_chain()
        back_text = []

        while True:
            back_text.append(seed_chain[0])
            if seed_chain[0][-1] in ['.', '!']:
                break
            del seed_chain[0]
            key = tuple(seed_chain)
            seed_chain.append(random.choice(self.cache[key]))

        self.cache = {}
        self.words.reverse()
        self.database()

        seed_chain = self.build_chain()
        front_text = []

        while True:
            front_text.append(seed_chain[0])
            if seed_chain[1][-1] in ['.', '!']:
                front_text.reverse()
                break
            del seed_chain[0]
            key = tuple(seed_chain)
            seed_chain.append(random.choice(self.cache[key]))

        self.cache = {}
        self.words.reverse()
        self.database()

        gen_text = front_text[:-1] + back_text
        if not gen_text[0][0].isupper():
            gen_text[0] = gen_text[0].capitalize()

        return ' '.join(gen_text)
