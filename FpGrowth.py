import operator
from collections import defaultdict
import json
from Queue import Queue
import datetime
import sys
import os
import re

class ItemNode:
	"""
	FP hash tree node.
	links: edges hashed by name
	prev: previous node up the tree.
	"""
	def __init__(self,name,prev):
		self.name=name
		self.count=1
		self.links=dict()
		self.prev=prev


def fp_growth(path,min_freq):
	"""
	run fp growth, save results to json file.
	"""

	#parse dare

	item_dict, transaction_list = get_items_and_transactions(path=path)
	#build FP tree
	item_map,fp_root = build_tree(item_dict, transaction_list,min_freq)

	#mine subsets from tree
	results=dict()
	mine_subsets(item_dict,item_map,min_freq,[],results,fp_root)

	#print and save results
	save_results(path,results,min_freq)

def save_results(path,results,min_freq):
	"""
	save results dict to json file.
	"""

	#create path
	if not os.path.isdir('results'):
		os.mkdir('results')

	pattern = re.compile(r'[^\/]*$')
	m = re.search(pattern, path)
	if m:
		output_path = 'results/%s_%d_%s.json'%(m.group(0),min_freq,str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
	else:
		output_path = 'results/%d_%s.json'%(min_freq,str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))

	#print grouping count
	for i in results:
		print '%d - %d'%(i,len(results[i]))
	
	#add metadata
	result_json = {'sets':results,'path':path, 'min_freq':min_freq}

	#dump json
	with open(output_path,'w') as fp:
	    json.dump(result_json, fp,indent=4)



def get_items_and_transactions(path):
	"""
	loads transaction and count frequency for each item.

	- saves transactions as a set (no weight based on # of item in a single transaction)
	- returns unordered transaction list
	- returns single freq dict: {item (int):frequency (int)}
	"""

	transaction_list = list()
	item_dict = defaultdict(int)

	#iterate over data
	with open(path) as f:
	    for line in f:
	    	#create transaction set
	    	transaction = set([int(item) for item in line.split(' ') if item.isdigit()])
	    	#add to transaction list
	    	transaction_list.append(transaction)
	    	#update item_dict, increase count for each item by 1
	    	for item in transaction:
	       		item_dict[item]=item_dict[item]+1
	
	print 'Done collecting transaction. %d transactions and %d unique items\n'%(len(transaction_list),len(item_dict))
	return item_dict, transaction_list


def transaction_to_ordered_stack(transaction,item_dict,min_freq):
	"""
	return a stack (implemented by list) with the transaction items.
	the stack is sorted by 1.frequency 2. name.
	first out - highest frequency-name
	"""
	transaction_tupples = list()
	#tupple items with frequencies
	for item in transaction:
		if item_dict[item]>=min_freq:
			transaction_tupples.append((item,item_dict[item]))
	
	#sort tupples by 1.frequency 2. name
	ordered_tupples = sorted(transaction_tupples, key = operator.itemgetter(1,0))
	#create item stack
	transaction_stack = [i[0] for i in ordered_tupples]
	
	return transaction_stack


def build_tree(item_dict, transaction_list,min_freq):
	"""
	builds initial FP-tree according to transactions,
	each transaction sorted by item's frequency.
	"""

	#build tree root
	root = ItemNode(None,None)

	#build item table (map from table to all node instances). 
	#traditionally implemented by a linked list
	item_map=dict()
	for item in item_dict:
		if item_dict[item]>=min_freq:
			item_map[item]=list()

	#build tree- for each transaction run down from node.
	for transaction in transaction_list:
		transaction_stack = transaction_to_ordered_stack(transaction,item_dict,min_freq)
		add_transaction_to_node(root,transaction_stack,item_map)

	return item_map,root


def add_transaction_to_node(node,transaction_stack,item_map):
	"""
	recursively adds a single transaction to node.
	"""
	#recursion condition
	if len(transaction_stack)==0:
		return
	#draw item from stack
	item = transaction_stack.pop()
	#connect to tree
	if item in node.links:
		node.links[item].count=node.links[item].count+1
	else:
		node.links[item]=ItemNode(item,node)
		item_map[item].append(node.links[item])
	#recursive call
	add_transaction_to_node(node.links[item],transaction_stack,item_map)


def sort_items(item_dict):
	"""
	takes frequency dict and return item list sorted by freq.
	"""
	item_tupples=[]
	for item in item_dict:
		item_tupples.append((item,item_dict[item]))

	#sort tupples by 1.frequency 2. name
	sorted_items = sorted(item_tupples, key = operator.itemgetter(1,0))
	sorted_items_only = [i[0] for i in sorted_items] 
	return sorted_items_only


def mine_subsets(item_dict,item_map,min_freq,suffix,results,root):
	"""
	recursively mine subsets from FP tree.
	"""
	#sort items by item_dict
	sorted_items=sort_items(item_dict)
		
	#build conditional pattern base and prefix tree
	new_root=ItemNode(None,None)

	for item in sorted_items:
		#thresholding by min freq for subsets and next level.
		if item_dict[item]>=min_freq:
			subset=suffix+[item]
			if not len(subset) in results:
				results[len(subset)]=[]
			#save subset
			results[len(subset)].append((str(subset),item_dict[item]))

			#patterns and prefix tree for next level.
			conditional_patterns(item,item_map,suffix+[item],min_freq,results,new_root)


def conditional_patterns(item,item_map,suffix,min_freq,results,root):
	"""
	extract patterns from prefix tree
	"""

	#build conditional pattern base
	patterns=list()
	#iterate over all instances of this item in the tree
	for node in item_map[item]:
		#climb up to the root to find pattern
		runner=node.prev
		path_stack=list()
		while runner.name!=None:
			#add node to pattern
			path_stack.append(runner.name)
			#update pointer
			runner=runner.prev
		#tupple pattern with the node's count.
		patterns.append((path_stack,node.count))

	#use patterns to build the next subtree
	build_sub_tree(item,patterns,None,suffix,min_freq,results)


def build_sub_tree(item,patterns,tupples_map,suffix,min_freq,results):
	"""
	uses patterns to construct prefix tree,
	mines the treerecursively.
	"""
	sub_tree_root = ItemNode(None,None)

	#nodes table
	sub_tree_item_map=dict()

	#build tree
	for stack in patterns:
		add_pattern_to_node(sub_tree_root,stack,sub_tree_item_map)
	
	#counts frequencies in prefix tree
	pattern_item_freq = BFS_frequencies(sub_tree_root,item)

	#mine tree and build next level tree.
	mine_subsets(pattern_item_freq,sub_tree_item_map,min_freq,suffix,results,sub_tree_root)


def add_pattern_to_node(node,stack,item_map):
	"""
	recursively adds pattern to node.
	"""
	if len(stack[0])==0:
		#node.count+=stack[1]
		return
	#draw item from stack and add to tree
	item = stack[0].pop()
	if item in node.links:
		node.links[item].count=node.links[item].count+stack[1]
	else:
		node.links[item]=ItemNode(item,node)
		node.links[item].count=stack[1]
		#link table to new item
		if not item in item_map:
			item_map[item]=list()
		item_map[item].append(node.links[item])
	
	#recursive call
	add_pattern_to_node(node.links[item],stack,item_map)


def BFS_frequencies(root,item):
	"""
	runs BFS on a directed graph and return frequency dict
	The BFS is Queue based.
	"""
	temp_freq=defaultdict(int)
	q=Queue()
	q.put(root)
	while not q.empty():
		v=q.get()

		for name,u in v.links.iteritems():
			if u.name!= item:
				temp_freq[u.name]=temp_freq[u.name]+u.count
			q.put(u)

	return temp_freq


def main():
	if len(sys.argv) != 3:
		print 'Aborting. 2 arguments required (transaction_file, min_freq)'
		return
	
	path, min_freq=sys.argv[1],sys.argv[2]
	
	if not os.path.isfile(path) or not min_freq.isdigit() or int(min_freq)<=1:
		print 'Aborting, invalid input.'
		return
		
	fp_growth(path,int(min_freq))


if __name__ == '__main__':
	main()













