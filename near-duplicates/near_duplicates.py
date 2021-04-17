import csv
import re
import nltk
from nltk import ngrams

shingles = {}
shingle_id = {}
i = 0

filename = open("./dataset/250K_lyrics_from_MetroLyrics.csv")
reader = csv.reader(filename, delimiter=",")
next(reader)
results = open('./250K__test_sets_for_LSH.tsv', 'w', newline='')
writer = csv.writer(results, delimiter='\t')
writer.writerow(['ID', 'ELEMENTS_IDS'])
for row in reader:
    lyrics = (re.sub(r'[^\w\s]', ' ', row[5])).lower().split()
    if len(lyrics) < 3:
        threegrams = ()
        for item in lyrics:
            threegrams = threegrams+(item,)
    else:
        threegrams = ngrams(lyrics, 3)

    for grams in threegrams:
        if str(grams) not in shingle_id.keys():
            shingle_id[str(grams)] = i
            i += 1

        if row[0] in shingles.keys():
            if shingle_id[str(grams)] not in shingles[row[0]]:
                shingles[row[0]].append(shingle_id[str(grams)])
        else:
            shingles[row[0]] = [shingle_id[str(grams)]]
    if row[0] not in shingles.keys():
        shingles[row[0]] = []
    writer.writerow([row[0], shingles[row[0]]])  # write in tsv file
filename.close()
results.close()
