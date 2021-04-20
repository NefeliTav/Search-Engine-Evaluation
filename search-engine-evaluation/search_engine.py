from whoosh.analysis import *
from whoosh.index import create_in
from whoosh.qparser import *
from whoosh.fields import *
from whoosh import scoring
from whoosh import index
import csv
import statistics
import numpy as np
import matplotlib.pyplot as plt
import math
import itertools


def mrr(gt, se):
    sum = 0
    for query_id in se:  # for each query
        rank = 0  # find position of first relevant result
        for doc_id in se[query_id]:  # for each document in results
            if query_id in gt.keys():  # avoid getting a keyerror
                if doc_id in gt[query_id]:  # it is indeed a relevant document
                    sum += 1/(rank+1)  # accumulate sum from all queries
                    # print(doc_id, query_id)
                    break  # i found first relevant,go to the next query
            rank += 1
    # print("----------------------------")
    return 1/(len(gt))*sum


def pak(gt, se, k, q):
    if q not in gt.keys():  # if query not in ground truth, exit
        return -1
    eval = 0
    i = 0
    for doc_id in se[q]:  # for each document in results
        if i < k:  # check first k docs
            if q in gt.keys():  # avoid getting a keyerror
                if doc_id in gt[q]:  # it is indeed a relevant document
                    eval += 1  # increment counter
            i += 1  # go to next doc
    if q in gt.keys():  # if query in ground truth
        return eval/min(k, len(gt[q]))
    return -1


def r_precision(gt, se, q):
    if q not in gt.keys():  # if query not in ground truth, exit
        return -1
    eval = 0
    i = 0
    for doc_id in se[q]:
        if i < len(gt[q]):
            if q in gt.keys():
                if q in gt.keys():
                    if doc_id in gt[q]:
                        # print(q, doc_id)
                        eval += 1
            i += 1
    if q in gt.keys():
        # print(eval/len(gt[q]))
        # print("===========================================")
        return eval/len(gt[q])
    return -1


def ndcgak(gt, se, k, q):
    if q not in gt.keys():  # if query not in ground truth, exit
        return -1
    dcg = 0.0
    relevance = 0.0
    i = 1
    for doc_id in se[q]:  # for each document in results
        if i <= k:  # check first k docs
            if q in gt.keys():  # avoid getting a keyerror
                if doc_id in gt[q]:  # it is indeed a relevant document
                    relevance = 1 / math.log2(i+1)
                else:
                    relevance = 0.0
                dcg += relevance  # accumulate relevance -> dcg
            i += 1  # go to next doc
    i = 1
    idcg = 0.0
    if q in gt.keys():  # avoid getting a keyerror
        for i in range(1, len(gt[q])+1):
            if i <= k:
                # ideal situation -> first k docs are relevant/in ground truth
                idcg += 1 / math.log2(i+1)
    if idcg != 0.0:
        return dcg/idcg
    return -1


# Open ground truth file
filename = open("./Cranfield_DATASET/cran_Ground_Truth.tsv")
ground_truth = csv.reader(filename, delimiter="\t")
next(ground_truth)
gt = {}  # save ground truth in a dictionary, in order to save time
for row in ground_truth:
    if row[0] in gt.keys():
        gt[row[0]].append(row[1])
    else:
        gt[row[0]] = [row[1]]
filename.close()
# print(gt)

query = {}  # dictionary with key=query_id and value=query
filename = open("./Cranfield_DATASET/cran_Queries.tsv")
csv_reader = csv.reader(filename, delimiter='\t')
# to skip the header: first line containing the name of each field.
csv_reader.__next__()
for record in csv_reader:
    query[record[0]] = record[1]
filename.close()


configurations = {0: [SimpleAnalyzer(), scoring.Frequency(), "SimpleAnalyzer, Frequency"],
                  1: [SimpleAnalyzer(), scoring.TF_IDF(), "SimpleAnalyzer, TF_IDF"],
                  2: [SimpleAnalyzer(), scoring.BM25F(), "SimpleAnalyzer, BM25F"],
                  3: [StandardAnalyzer(), scoring.TF_IDF(), "StandardAnalyzer, TF_IDF"],
                  4: [StandardAnalyzer(), scoring.BM25F(), "StandardAnalyzer, BM25F"],
                  5: [StemmingAnalyzer(), scoring.TF_IDF(), "StemmingAnalyzer, TF_IDF"],
                  6: [StemmingAnalyzer(), scoring.BM25F(), "StemmingAnalyzer, BM25F"],
                  7: [KeywordAnalyzer(lowercase=True), scoring.TF_IDF(), "KeywordAnalyzer, TF_IDF"],
                  8: [KeywordAnalyzer(lowercase=True), scoring.BM25F(), "KeywordAnalyzer, BM25F"],
                  9: [FancyAnalyzer(), scoring.TF_IDF(), "FancyAnalyzer, TF_IDF"],
                  10: [FancyAnalyzer(), scoring.BM25F(), "FancyAnalyzer, BM25F"],
                  11: [LanguageAnalyzer("en"), scoring.BM25F(), "LanguageAnalyzer, BM25F"],
                  }

mean = {}  # dictionary with mrr for each search engine
temp = 0  # index of each search engine
r_mean = {}  # mean r-precision for each search engine
r_prec = {}  # all r-precisions for each search engine
max_ = {}  # dictionary with max r-precision for each search engine
min_ = {}  # dictionary with min r-precision for each search engine
all_se = {}  # dictionary of dictionaries containing the search results


for conf in range(len(configurations)):
    # Define a Text-Analyzer
    selected_analyzer = configurations[conf][0]
    # Create a Schema
    schema = Schema(id=ID(stored=True), content=TEXT(
        stored=False, analyzer=selected_analyzer))

    # Create an empty-Index according to the just defined Schema
    directory_containing_the_index = './index'
    create_in(directory_containing_the_index, schema)
    ix = index.open_dir(directory_containing_the_index)

    num_docs = 0
    # Fill the Index

    writer = ix.writer()
    for x in range(1, 1401):  # for every html file
        html_files = "./Cranfield_DATASET/DOCUMENTS/______"+str(x)+".html"
        num_docs += 1
        id = str(x)
        # print(id)
        with open(html_files, "r", encoding='latin1') as filename:
            file_data = filename.readline()
            # i dont care about the info before <body>
            while(file_data.startswith('<body>') == False):
                file_data = filename.readline()
            content = ''
            while(file_data != '</body>\n'):  # i stop when body ends
                file_data = filename.readline()

                content += file_data
            # print(content)
            writer.add_document(id=id, content=content)

        # print("-----------------------------------")
    writer.commit()
    filename.close()

    # Select a Scoring-Function
    scoring_function = configurations[conf][1]

    temp += 1  # count search engines

    # Create a QueryParser for parsing the input_query
    qp = QueryParser("content", ix.schema)

    # Create a Searcher for the Index with the selected Scoring-Function
    searcher = ix.searcher(weighting=scoring_function)

    # Create tsv file to save results (all possible combinations of queries and documents)
    with open('./search_engines/results'+str(temp)+'.tsv', 'w', newline='') as filename:
        writer = csv.writer(filename, delimiter='\t')
        writer.writerow(['Query_ID', 'Doc_ID', 'Rank', 'Score'])
        se = {}  # save search engine results in dictionary to save time
        sum_r = 0
        min_r = float("inf")
        max_r = float("-inf")
        tmp = 0
        for x in range(1, 226):  # for each query
            if str(x) in query:  # make sure that i dont get a keyerror e.g. 31 doesn't exist
                input_query = query[str(x)]
                parsed_query = qp.parse(input_query)  # parsing the query
                # Perform a Search
                results = searcher.search(parsed_query)
                # Save results in tsv file
                for hit in results:
                    writer.writerow(
                        [str(x), hit['id'], str(hit.rank + 1), str(hit.score)])
                    if str(x) in se.keys():
                        se[str(x)].append(hit['id'])
                    else:
                        se[str(x)] = [hit['id']]
                # print(temp,str(x),pak(gt, se, k,str(x)))

                tmp = r_precision(gt, se, str(x))
                if tmp != -1:  # -1 if not in ground truth
                    if temp in r_prec.keys():
                        r_prec[temp].append(tmp)
                    else:
                        r_prec[temp] = [tmp]
                    sum_r += tmp
                    if tmp > max_r:
                        max_r = tmp
                    if tmp < min_r:
                        min_r = tmp
        max_[temp] = max_r
        min_[temp] = min_r
        r_mean[temp] = sum_r/len(gt)
        all_se[temp] = se

    mean[temp] = mrr(gt, se)
    # print(temp, mean[temp])
    filename.close()
    searcher.close()


med = {}
quar1 = {}
quar3 = {}

print("MRR:")
print(mean)
print("--------------")
print("Mean R-precision:")
print(r_mean)
print("--------------")
print("Max R-precision:")
print(max_)
print("--------------")
print("Min R-precision:")
print(min_)
print("--------------")
for conf in r_prec:
    med[conf] = statistics.median(sorted(r_prec[conf]))
    quar1[conf] = np.percentile(r_prec[conf], 25)
    quar3[conf] = np.percentile(r_prec[conf], 75)
    # print("median",np.percentile(r_prec[conf], 50)) #check that median is correct
print("1st quartile: ")
print(quar1)
print("--------------")
print("3rd quartile: ")
print(quar3)
print("--------------")
print("Median R-precision:")
print(med)

sorted_mrr = {k: v for k, v in sorted(
    mean.items(), key=lambda x: x[1], reverse=True)}  # sort by mrr
sorted_mrr = dict(itertools.islice(sorted_mrr.items(), 5)
                  )  # take top five search engines
print("--------------")
print("Top 5 search engine configurations:")
print(sorted_mrr)

y = {}

X = 1.0
x = [1, 3, 5, 10]
plt.xlabel("k")
plt.ylabel("average p@k")
plt.title("Average p@k for top 5 search engines")
for key, se in all_se.items():  # key = search engine index
    if key in sorted_mrr:  # search engine is in top five
        total1 = 0
        total2 = 0
        total3 = 0
        total4 = 0
        # print(key)
        for q in se:  # for every query
            result1 = pak(gt, se, 1, q)  # k = 1
            result2 = pak(gt, se, 3, q)  # k = 3
            result3 = pak(gt, se, 5, q)  # k = 5
            result4 = pak(gt, se, 10, q)  # k = 10

            if result1 != -1:  # if result = -1 ,that means thats the query doesnt exist in ground truth
                total1 += result1
            if result2 != -1:
                total2 += result2
            if result3 != -1:
                total3 += result3
            if result4 != -1:
                total4 += result4

        #print(total1, total2, total3, total4, len(gt))
        plt.plot(x, [total1/len(gt), total2/len(gt), total3/len(gt),
                 total4/len(gt)], label="search engine no "+str(key), marker='o')
plt.legend()
plt.xticks(np.arange(min(x), max(x)+1, X))
plt.show()


plt.xlabel("k")
plt.ylabel("average nDCG")
plt.title("Average nDCG for top 5 search engines")
for key, se in all_se.items():
    if key in sorted_mrr:
        total1 = 0
        total2 = 0
        total3 = 0
        total4 = 0
        for q in se:
            result1 = ndcgak(gt, se, 1, q)
            result2 = ndcgak(gt, se, 3, q)
            result3 = ndcgak(gt, se, 5, q)
            result4 = ndcgak(gt, se, 10, q)
            if result1 != -1:
                total1 += result1
            if result2 != -1:
                total2 += result2
            if result3 != -1:
                total3 += result3
            if result4 != -1:
                total4 += result4
        # print(total1,total2,total3,total4)
        plt.plot(x, [total1/len(gt), total2/len(gt), total3/len(gt),
                 total4/len(gt)], label="search engine no "+str(key), marker='o')
plt.legend()
plt.xticks(np.arange(min(x), max(x)+1, X))
plt.show()
print("--------------")
print("Indexed documents:")
print(num_docs)
print("Number of queries:")
print(len(query))
print("Number of queries in ground truth:")
print(len(gt))
