from whoosh.analysis import SimpleAnalyzer
from whoosh.index import create_in
from whoosh.qparser import *
from whoosh.fields import *
from whoosh import scoring
from whoosh import index
import csv

# Define a Text-Analyzer 
selected_analyzer = SimpleAnalyzer()

# Create a Schema 
schema = Schema(id=ID(stored=True), content=TEXT(stored=False, analyzer=selected_analyzer))

# Create an empty-Index according to the just defined Schema
directory_containing_the_index = './temp'
create_in(directory_containing_the_index, schema)
ix = index.open_dir(directory_containing_the_index)

# Fill the Index
writer = ix.writer()
for x in range(1,1401):     #for every html file
    html_files = "./Cranfield_DATASET/DOCUMENTS/______"+str(x)+".html"
    id = str(x)
    #print(id)
    with open(html_files, "r", encoding='latin1') as filename:
        file_data = filename.readline()
        while(file_data.startswith('<body>') == False): #i dont care about the info before <body>
            file_data = filename.readline()
        content = ''
        while(file_data != '</body>\n'):  #i stop when body ends
            file_data = filename.readline()
            if (file_data != '</body>\n'):
                content += file_data
        #print(content)
        writer.add_document(id=id, content=content)
    #print("-----------------------------------")
writer.commit()
filename.close()

query = {}  #dictionary with key=query_id and value=query
filename = open("./Cranfield_DATASET/cran_Queries.tsv")
csv_reader = csv.reader(filename, delimiter='\t')
csv_reader.__next__()  # to skip the header: first line containing the name of each field.
for record in csv_reader:
    query[record[0]] = record[1]

input_query = query['1']
max_number_of_results = 5

# Select a Scoring-Function
scoring_function = scoring.Frequency()

# Create a QueryParser for parsing the input_query.
qp = QueryParser("content", ix.schema)
parsed_query = qp.parse(input_query)  # parsing the query
print("Input Query : " + input_query)
print("Parsed Query: " + str(parsed_query))

# Create a Searcher for the Index with the selected Scoring-Function 
searcher = ix.searcher(weighting=scoring_function)

# Perform a Search 
results = searcher.search(parsed_query, limit=max_number_of_results)

print()
print("Rank" + "\t" + "DocID" + "\t" + "Score")
for hit in results:
    print(str(hit.rank + 1) + "\t" + hit['id'] + "\t" + str(hit.score))
searcher.close()

print()
