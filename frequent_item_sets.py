from collections import defaultdict
import itertools
from datetime import datetime

def get_items_and_transactions(path='data/retail_25k.dat'):
	"""
	load data, extracts all transaction.
	return transaction list and a set of all unique items (k=1)
	"""
	transaction_list = list()
	item_set = set()
	with open(path) as f:
	    for line in f:
	    	transaction = frozenset([int(item) for item in line.split(' ') if item.isdigit()])
	    	#print transaction
	    	transaction_list.append(transaction)
	    	for item in transaction:
	       		item_set.add(frozenset([item])) 
	print 'Done collecting transaction. %d transactions and %d unique items\n'%(len(transaction_list),len(item_set))
	return item_set, transaction_list



def prune_and_return_items(item_set, transaction_list, min_freq,k,open_transactions,transaction_track):
	"""
	for each set in item_set (level k),
	counts frequency of appearances in transactions
	and prunes every set that doesn't meet min_freq.
	"""
	prune_start_time = datetime.now()	# used for logging and some optimizations.
	pruned_item_set = set()				# all sets with freq>min_freq.
	localSet = defaultdict(int)			# frequency counter for all sets in level.
	open_transactions_num=0				# counts transactions that can still contribute sets.

	for idx,transaction in enumerate(transaction_list):
		#check if transaction had a set in level k-1
		if not open_transactions[idx]:
			continue
		else:
			open_transactions[idx]=False
		#case one- item_set is short (shorter list optimization)
		if len(transaction_track)>0 and (len(item_set)<transaction_track[k-2]):
			for item in item_set:
				if item.issubset(transaction):
					localSet[item] += 1
					open_transactions[idx]=True
		#case one- item_set is long, better to iterate over permutations 
		else:
			combs= itertools.combinations(transaction,k)
			for comb in combs:
				current = frozenset(comb)
				if current in item_set:
					localSet[current] += 1
					open_transactions[idx]=True

		if open_transactions[idx]:
			open_transactions_num+=1

	transaction_track.append(open_transactions_num)
	for item, freq in localSet.items():
		if freq >= min_freq:
			pruned_item_set.add(item)
	
	print 'Done pruning level k=%d,'%k
	print '%d out of %d items passed min_freq (%d).'%(len(pruned_item_set),len(item_set),min_freq)
	print 'iteration time: %s seconds'%str((datetime.now()-prune_start_time).seconds)
	print 'number of transactions: %d of %d.\n'%(open_transactions_num,len(open_transactions))

	return pruned_item_set


def apriori(path,min_freq):

	#get data, build initial stractures for items and transactions.
	item_set,transaction_list = get_items_and_transactions(path)
	open_transactions=[True]*len(transaction_list)
	transaction_track=[]
	#initialize dictionary that will hold all valid sets
	L = dict()
	
	#prune singles set with respect to min_freq
	L_1 = prune_and_return_items(item_set, transaction_list, min_freq,1,open_transactions,transaction_track)
	
	#k is the size of sets in each iteration
	k = 2
	L_k = L_1	

	#iterate over k values and find frequent set
	while(len(L_k)!=0):
		#save k-1 valid sets
		L[k-1] = L_k		
		C_k = next_k_level_sets(L_k,k)
		L_k = prune_and_return_items(C_k, transaction_list, min_freq,k,open_transactions,transaction_track)
		k+=1

	print L

def next_k_level_sets(L_k,k):
	start_time = datetime.now()
	C_k=set()
	for i,i_set in enumerate(L_k):
		for j,j_set in enumerate(L_k):
			if j>i:
				candidate_set = i_set.union(j_set)
				if len(candidate_set)==k:
					C_k.add(candidate_set)
	#old version (time and memory optimization):
	#C_k = set([i.union(j) for i in L_k for j in L_k if len(i.union(j)) == k])
	print 'level %d generation: %s seconds'%(k,str((datetime.now()-start_time).seconds))
	return C_k


apriori(path='data/retail_25k.dat',min_freq=200)



