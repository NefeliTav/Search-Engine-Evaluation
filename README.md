# Search Engine Evaluation
python3 search_engine.py \
I implemented 12 search engines , with different combinations of analyzers and scoring functions.
After indexing a collection of documents (html files) , i check the search engines in order to find the one with the best performance,
namely the one with the most relevant results (ground truth).For this i use some standard algorithms,like p@k, mean reciprocal rank, r-precision, nDCG@k.
In the .tex file ,there is a report , where i present some statistics concerning the search engine configuartions, mean,median,min,max,1st and 3rd quartile.
Also, for each search engine ,a .tsv file is created that contains the results of the search.
