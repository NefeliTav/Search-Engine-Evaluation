## Search Engine Evaluation

This program implements 12 search engines , with different combinations of analyzers and scoring functions ,using the Whoosh library.
After indexing a collection of documents (html files) , it checks the search engines in order to find the one with the best performance,
namely the one with the most relevant results (comparing the results to the ground truth). For this, some standard algorithms are used,like p@k, mean reciprocal rank, r-precision, nDCG@k.
In the .tex file ,there is a report , where some statistics are presented concerning the search engine configuartions.
Also, for each search engine ,a .tsv file is created that contains the results of the search.

To find the best search engines :
```
python search_engine.py
```

## Near-Duplicate Detection

This program finds near-duplicates according to the lyrics of 250K songs, by creating shingles,min-hashing sketches and lsh, using some java tools.

To perform shingling :
```
python near_duplicates.py
```

To create min-hashing sketches and perform lsh:
```
java -Xmx3G tools.NearDuplicatesDetector lsh_plus_min_hashing 0.95 20 15 ./data/300.tsv ./data/results.tsv ./data/near_duplicates.tsv
```
