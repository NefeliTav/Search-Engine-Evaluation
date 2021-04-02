from whoosh.analysis import SimpleAnalyzer
from whoosh.analysis import StandardAnalyzer
from whoosh.analysis import StemmingAnalyzer
from whoosh.analysis import KeywordAnalyzer
from whoosh.analysis import FancyAnalyzer
from whoosh.analysis import LanguageAnalyzer
from whoosh.analysis import NgramAnalyzer
from whoosh.analysis import NgramWordAnalyzer


from whoosh.index import create_in
from whoosh.qparser import *
from whoosh.fields import *
from whoosh import scoring
from whoosh import index
import csv

def evaluator (gt ,se ,k):
    for query_id in se:
        eval = 0
        i = 0
        print(query_id)
        for doc_id in se[query_id]:
            if i < k:
                if query_id in gt.keys():
                    if doc_id in gt[query_id]:
                        eval += 1
            i += 1
        #print("\teval = ",eval)
    #print("--------------")
        print("\t",eval/min(k,len(gt)))
    return eval/min(k,len(gt))

k = 5

# Open ground truth file
filename = open("./Cranfield_DATASET/cran_Ground_Truth.tsv")
ground_truth = csv.reader(filename, delimiter="\t")
next(ground_truth)
gt = {} #save ground truth in a dictionary, in order to economize time
for row in ground_truth:
    if row[0] in gt.keys():
        gt[row[0]].append(row[1])
    else:
        gt[row[0]] = [row[1]]
filename.close()
#print(gt)


analyzers = [SimpleAnalyzer(),StandardAnalyzer(),StemmingAnalyzer(),KeywordAnalyzer(),FancyAnalyzer(),LanguageAnalyzer("en")]

scoring = [scoring.Frequency(),scoring.TF_IDF(),scoring.BM25F()]

temp = 0
# Define a Text-Analyzer 
for selected_analyzer in analyzers:
    # Create a Schema 
    schema = Schema(id=ID(stored=True), content=TEXT(stored=False, analyzer=selected_analyzer))

    # Create an empty-Index according to the just defined Schema
    directory_containing_the_index = './index'
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
    filename.close()

    #max_number_of_results = 5

    # Select a Scoring-Function
    for scoring_function in scoring:
        if temp!=0 and scoring_function==scoring[0]:    #use frequency scoring only once
            continue
        temp+=1 #count search engines

        if temp > 12: #i want 12 search engines
            break

        # Create a QueryParser for parsing the input_query
        qp = QueryParser("content", ix.schema)

        # Create a Searcher for the Index with the selected Scoring-Function 
        searcher = ix.searcher(weighting=scoring_function)

        # Create tsv file to save results (all possible combinations of queries and documents)
        with open('results'+str(temp)+'.tsv', 'w', newline='') as filename:
            writer = csv.writer(filename , delimiter='\t')
            writer.writerow(['Query_ID','Doc_ID','Rank','Score'])
            se = {} #save search engine results in dictionary to economize time
            for x in range(1,226): #for each query
                if str(x) in query: #make sure that i dont get a keyerror
                    input_query = query[str(x)]
                    parsed_query = qp.parse(input_query)  # parsing the query

                    # Perform a Search 
                    results = searcher.search(parsed_query)#, limit=max_number_of_results)

                    # Save results in tsv file
                    for hit in results:
                        writer.writerow([str(x),hit['id'],str(hit.rank + 1),str(hit.score)])
                        if str(x) in se.keys():
                            se[str(x)].append(hit['id'])
                        else:
                            se[str(x)] = [hit['id']]
        evaluator(gt, se, k)
        filename.close()
    searcher.close()


