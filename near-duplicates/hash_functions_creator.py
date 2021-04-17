import random
import math
import csv

################################################
num_hash_functions = 300
upper_bound_on_number_of_distinct_elements  = 10000000
#upper_bound_on_number_of_distinct_elements  =  8685356
#upper_bound_on_number_of_distinct_elements =   138492
#upper_bound_on_number_of_distinct_elements =  3746518
n = str(upper_bound_on_number_of_distinct_elements)
################################################


### primality checker
def is_prime(number):
	if number == 2:
		return True
	if (number % 2) == 0:
		return False
	for j in range(3, int(math.sqrt(number)+1), 2):
		if (number % j) == 0: 
			return False
	return True



set_of_all_hash_functions = set()
while len(set_of_all_hash_functions) < num_hash_functions:
	a = random.randint(1, upper_bound_on_number_of_distinct_elements-1)
	b = random.randint(0, upper_bound_on_number_of_distinct_elements-1)
	p = random.randint(upper_bound_on_number_of_distinct_elements, 10*upper_bound_on_number_of_distinct_elements)
	while is_prime(p) == False:
		p = random.randint(upper_bound_on_number_of_distinct_elements, 10*upper_bound_on_number_of_distinct_elements)
	#
	current_hash_function_id = tuple([a, b, p])
	set_of_all_hash_functions.add(current_hash_function_id)

filename = open('./hash_functions/300.tsv','w',newline='')
writer = csv.writer(filename , delimiter='\t')
writer.writerow(('a','b','p','n'))
#print("a\tb\tp\tn")
for a, b ,p in set_of_all_hash_functions:
	writer.writerow((a,b,p,n)) #write in tsv file #str(upper_bound_on_number_of_distinct_elements))
filename.close()

