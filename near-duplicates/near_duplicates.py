import csv
import re

shingles = {}
punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

filename = open("../dataset/250K_lyrics_from_MetroLyrics.csv")
reader = csv.reader(filename, delimiter = ",")
next(reader)
for row in reader:
    i = 0
    lyrics = (re.sub(r'[^\w\s]','',row[5])).lower().split()
    length = len(lyrics)

    while(i < length - 2):
        if row[0] in shingles.keys():
            shingles[row[0]].append([lyrics[i],lyrics[i+1],lyrics[i+2]])
        else:
            shingles[row[0]] = [[lyrics[i],lyrics[i+1],lyrics[i+2]]]
        i += 1
    if row[0] not in shingles.keys():
        shingles[row[0]] = []
    #print(shingles[row[0]])
    #print("----------------------------------------------------------------")
filename.close()
