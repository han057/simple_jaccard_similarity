import csv
import pprint
import logging
import random
from nltk.corpus import stopwords

def loadStopWords():
    return tuple(stopwords.words('english'))

def loadShingles(file, stop_word_tuple):
    universal_shingles = set()
    shingles_per_file = dict()
    
    for l in file:
        article_shingles = set()
        words = l.split(' ')
        for i in range(1, len(words)):
            logging.debug("[+] Checking if the word is a stop word...")
            if words[i].lower() in stop_word_tuple:
                logging.debug("[+] The word is a stop word!")
                shingle = words[i] + ' ' +  words[i + 1] if((i+1)<=len(words)) else '' + ' ' + words[i + 2] if (i+1)<=len(words) else ''
                logging.debug("[+] Checking if the shingle is not in the article shingles")
                if shingle not in article_shingles:
                    logging.debug("[+] The shingle is not in the article shingles, adding it...")
                    article_shingles.add(shingle)
                    logging.debug("[+] Checking if the shingle is not in the universe of shingles")
                    if shingle not in universal_shingles:
                        logging.debug("[+] The shingle is not in the universe of shingles, adding it...")
                        universal_shingles.add(shingle)
        logging.debug("[+] Adding new tuple to the golder of every file shingles")
        shingles_per_file[words[0]] = article_shingles
    return (list(universal_shingles), shingles_per_file)            

def buildHashFunction(a, b, c):
    def hashFunction(x):
        return (a*x+b)%c
    return hashFunction




stop_word_tuple = loadStopWords()
with open('dataset_1.txt') as f:
    universal_shingles, shingles_per_file_dict = loadShingles(f, stop_word_tuple)


print("""
******************************************
Numbers of articles [{}]
Shingle unverse size [{}]
******************************************
""".format(len(shingles_per_file_dict), len(universal_shingles)))

print(universal_shingles[0])
print(universal_shingles[535])

a = random.randint(0, 1000)    
b = random.randint(0, 1000)
c = 5563

print("""
******************************************
a = {}
b = {}
c = {}
******************************************
""".format(a, b, c))

