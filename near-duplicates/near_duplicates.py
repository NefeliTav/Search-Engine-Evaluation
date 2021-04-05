import csv
import re
import nltk
from nltk import ngrams

shingles = {}
temp = {}
i = 0

punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

filename = open("../dataset/250K_lyrics_from_MetroLyrics.csv")
reader = csv.reader(filename, delimiter = ",")
next(reader)
for row in reader:
    lyrics = (re.sub(r'[^\w\s]','',row[5])).lower().split()
    threegrams = ngrams(lyrics , 3)

    for grams in threegrams:
        if str(grams) not in temp.keys():
            temp[str(grams)] = i
            i += 1

        if row[0] in shingles.keys():
            if temp[str(grams)] not in shingles[row[0]]:
                shingles[row[0]].append(temp[str(grams)])
        else:
            shingles[row[0]] = [temp[str(grams)]]
    print(row[0],shingles[row[0]])
    print("-------------------------------------------------")
    s = input()
filename.close()
