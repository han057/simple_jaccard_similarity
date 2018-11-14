import csv
import pprint
import logging
import random
from nltk.corpus import stopwords
import numpy as np
import time

logging.basicConfig(level=logging.DEBUG)


def buildHashFunction(a, b, c):
    def hashFunction(x):
        return (a*x+b) % c
    return hashFunction


def hashFunctionsSet(primeNumber, numberOfFunctions):
    hashFunctions = list()
    for i in range(numberOfFunctions):
        a = random.randint(0, 10000)
        b = random.randint(0, 10000)
        hashFunctions.append(buildHashFunction(a, b, primeNumber))
    return hashFunctions


def loadStopWords():
    return tuple(stopwords.words('english'))


def loadShingles(file, stop_word_tuple):
    index = 0
    prime = 163
    numberOfHashFunctions = 10
    universal_shingles = list()
    hashFunctions = hashFunctionsSet(prime, numberOfHashFunctions)
    articles = file.read().split("\n")
    numberOfArticles = len(articles)
    #numberOfArticles = numberOfArticles // 10
    signatureMatrix = np.full((numberOfArticles, numberOfHashFunctions), prime)

    for a in range(numberOfArticles):
        article_shingles = set()
        words = articles[a].split(' ')
        numberOfWords = int(len(words)/4)
        for w in range(1, numberOfWords):
            if words[w].lower() in stop_word_tuple:
                shingle = words[w]
                if((w+2) <= numberOfWords):
                    shingle = words[w+1] + ' ' + words[w+2]
                try:
                    indexOfShingle = universal_shingles.index(shingle)
                except:
                    indexOfShingle = index
                    index += 1
                    universal_shingles.append(shingle)

                if indexOfShingle not in article_shingles:
                    article_shingles.add(indexOfShingle)
                    for h in range(numberOfHashFunctions):
                        bucket = hashFunctions[h](indexOfShingle)
                        if bucket < signatureMatrix[a][h]:
                            signatureMatrix[a][h] = bucket
    return (len(universal_shingles), numberOfArticles, signatureMatrix.T)


def calculateJaccardSimilarity(sm):
    print("Calculando jaccard similarity...")

    permutations = sm.shape[0]
    documents = sm.shape[1]
    jaccardResultMatrix = np.zeros((documents, documents))
    for i in range(documents):
        di = sm[:, i]
        for j in range(i + 1, documents):
            dj = sm[:, j]
            similarity = (di == dj).sum() / permutations
            jaccardResultMatrix[i][j] = similarity
    print(jaccardResultMatrix)


def main():
    with open('dataset_10.txt') as f:
        us, spf, sm = loadShingles(f, loadStopWords())

    print("""
    ******************************************
    Numbers of articles [{}]
    Shingle unverse size [{}]
    ******************************************
    """.format(spf, us))
    print(sm)
    calculateJaccardSimilarity(sm)

start = time.clock()
main()
print((time.clock() - start)/1000/60)
