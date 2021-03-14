from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import *
from whoosh.analysis import StandardAnalyzer
from whoosh import index
from whoosh import scoring
import csv
import time

#Define text-analyzer
analyzer = StandardAnalyzer()

# Create a Schema 
schema = Schema(id=ID(stored=True),content=TEXT(stored=False, analyzer=analyzer))

# Create an empty-Index according to the just defined Schema
directory_containing_the_index = './directory_index_SimpleAnalyzer'
create_in(directory_containing_the_index, schema)

current_time_msec = lambda: int(round(time.time() * 1000))
ix = index.open_dir(directory_containing_the_index)

# Fill the Index
print("TimeStamp: ", time.asctime(time.localtime(time.time())))
ts_start = current_time_msec()
writer = ix.writer()

ALL_DOCUMENTS_file_name = "./lyrics_dataset/first_10K_lyrics_from_MetroLyrics.csv"
in_file = open(ALL_DOCUMENTS_file_name, "r", encoding='latin1')
csv_reader = csv.reader(in_file, delimiter=',')
csv_reader.__next__()  # to skip the header: first line containing the name of each field.
num_added_records_so_far = 0
for record in csv_reader:
    id = record[0]
    song = record[1]
    #
    writer.add_document(id=id, content=song)
    #
    num_added_records_so_far += 1
    if (num_added_records_so_far % 1000 == 0):
        print(" num_added_records_so_far= " + str(num_added_records_so_far))

writer.commit()
in_file.close()

ts_end = current_time_msec()
print("TimeStamp: ", time.asctime(time.localtime(time.time())))
total_time_msec = (ts_end - ts_start)
print("total_time= " + str(total_time_msec) + "msec")

# Create a Query
input_query = 'love OR hate'

max_number_of_results = 5

# Select a Scoring-Function
scoring_function = scoring.TF_IDF()


# Create a QueryParser for parsing the input_query.
qp = QueryParser("content", ix.schema)
parsed_query = qp.parse(input_query)  # parsing the query
print("Input Query : " + input_query)
print("Parsed Query: " + str(parsed_query))

# Create a Searcher for the Index with the selected Scoring-Function 
searcher = ix.searcher(weighting=scoring_function)

# perform a Search
results = searcher.search(parsed_query, limit=max_number_of_results)

# print the ID of the best documents associated to the input query.
print()
print("Rank" + "\t" + "DocID" + "\t" + "Score")
for hit in results:
    print(str(hit.rank + 1) + "\t" + hit['id'] + "\t" + str(hit.score))
searcher.close()
print()