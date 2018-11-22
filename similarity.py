import sys
import getopt
import logging
import random
import time
import pprint

from decimal import Decimal
from nltk.corpus import stopwords
import numpy as np


def buildHashFunction(a, b, c):
    logging.debug("[Debug] Creating hash function...")

    def hashFunction(x):
        return (a*x+b) % c
    return hashFunction


def sieve_of_eratosthenes(max_integer, start_):
    sieve = [True for _ in range(max_integer + 1)]
    sieve[0:1] = [False, False]
    for start in range(max_integer + 1):
        if sieve[start]:
            for i in range(2 * start, max_integer + 1, start):
                sieve[i] = False

    prime = 0
    for i in range(start_, max_integer + 1):
        if sieve[i]:
            prime = i
            break
    return prime


def generateHashFunctions(primeNumber, numberOfFunctions):
    logging.debug("[Debug] Creating hash function list...")
    hashFunctions = list()
    for i in range(numberOfFunctions):
        a = random.randint(0, 10000)
        b = random.randint(0, 10000)
        hashFunctions.append(buildHashFunction(a, b, primeNumber))
    return hashFunctions


def loadStopWords():
    return tuple(stopwords.words('english'))


def loadCharacteristicsMatrix(file, stop_word_tuple):
    index = 0
    universal_shingles = dict()
    articles = file.read().split("\n")
    numberOfArticles = len(articles)
    logging.debug("[Debug] Number of articles [{}]".format(numberOfArticles))
    articlesAndShinglesIndexes = list()
    for a in range(numberOfArticles):
        progress = int(a/numberOfArticles*100)
        printProgress(progress + 1)
        article_shingles = set()
        words = articles[a].split(' ')
        numberOfWords = len(words)
        for w in range(1, numberOfWords):
            if words[w].lower() in stop_word_tuple:
                if((w+2) < numberOfWords):
                    shingle = words[w] + ' ' + words[w+1] + ' ' + words[w+2]
                #try:
                indexOfShingle = universal_shingles.get(shingle)
                if indexOfShingle is None:
                    indexOfShingle = index
                    universal_shingles[shingle] = indexOfShingle
                    index += 1
                #except:
                #    indexOfShingle = index
                #    index += 1
                #    universal_shingles.append(shingle)
                if indexOfShingle not in article_shingles:
                    article_shingles.add(indexOfShingle)
        articlesAndShinglesIndexes.append(article_shingles)
    return (articlesAndShinglesIndexes, len(universal_shingles))


def printProgress(progress):
    print("[+]{}{}> {}%".format(int(progress/2)*'=', int((100-progress)/2)*'-', progress), end="\r")


def loadSignatureMatrix(numberOfHashFunctions, characteristicsMatrix, prime):
    hashFunctions = generateHashFunctions(prime, numberOfHashFunctions)
    size = (len(characteristicsMatrix), numberOfHashFunctions)
    signatureMatrix = np.full(size, prime)
    for index, document in enumerate(characteristicsMatrix):
        progress = int(index/size[0]*100)
        printProgress(progress + 1)
        for h in range(numberOfHashFunctions):
            hashFunction = hashFunctions[h]
            for shingleIndex in document:
                bucket = hashFunction(shingleIndex)
                if bucket < signatureMatrix[index][h]:
                    signatureMatrix[index][h] = bucket
    return signatureMatrix.T


def calculateJaccardSimilarity(sm, threshold):
    permutations = sm.shape[0]
    documents = sm.shape[1]
    jaccardResultMatrix = np.zeros((documents, documents))
    maxSimilarity = list()
    for i in range(documents):
        printProgress(int(i/documents*100) + 1)
        di = sm[:, i]
        for j in range(i + 1, documents):
            dj = sm[:, j]
            similarity = (di == dj).sum() / permutations
            if similarity >= threshold:
                maxSimilarity.append((i, j, str(similarity)))
            jaccardResultMatrix[i][j] = similarity
    return (jaccardResultMatrix, maxSimilarity)


def usage():
    print("""\nUsage:\n
    similarity.py -f [file] -n [numberOfHashFunctions] -t [threshold]
    """)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "f:n:t:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(opts) != 3:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-f':
            file = arg
        elif opt in "-n":
            numberOfHashFunctions = int(arg)
        elif opt in "-t":
            threshold = float(arg)

    logging.debug("[Debug] opening file...")
    with open(file) as f:
        print("[+] Loading characteristics matrix...")
        cm, usLen = loadCharacteristicsMatrix(f, loadStopWords())
        print("\n[+] Done!")
        print("[+] Loading signature matrix...")
        prime = sieve_of_eratosthenes(usLen * 2, usLen)
        signatureMatrix = loadSignatureMatrix(numberOfHashFunctions, cm, prime)
        print("\n[+] Done!")
        print("[+] Calculating jaccard similarity...")
        jaccardResultMatrix, maxSimilarity = calculateJaccardSimilarity(signatureMatrix, threshold)
        print("\n[+] Done!")
        # print("\n[+] First 5 similar documents")
        # pprint.pprint(maxSimilarity[:5])

        print("""\n\n*************************************************
*        Numbers of articles         [{}]\t*
*        Shingle unverse size        [{}]\t*
*        Number of similar documents [{}]\t*
*************************************************\n\n""".format(len(cm), usLen, len(maxSimilarity)))
        print(maxSimilarity)

if __name__ == "__main__":
    start = time.clock()
    main(sys.argv[1:])
    print("{:.2f}s ".format((time.clock() - start)))
