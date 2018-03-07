""" Test Fragmentation index with data from Borgatti """
import networkx as nx

#
#
# 2 complete graphs a 5 nodes
A = nx.to_undirected(nx.complete_graph([1,2,3,4,5]))
B = nx.to_undirected(nx.complete_graph([6,7,8,9,10]))
# A=nx.to_undirected(A)
# B=nx.to_undirected(B)
c = nx.union(A,B)
ch = nx.harmonic_centrality(c)
print(ch)
print(sum(ch.values())/(nx.number_of_nodes(c)*(nx.number_of_nodes(c)-1)))
print(1. - (sum(ch.values())/(nx.number_of_nodes(c)*(nx.number_of_nodes(c)-1))))

#
#
# 2 path 1->2->3->4->5 and 6->7->8->9->10
a = nx.to_undirected(nx.path_graph([1,2,3,4,5]))
b = nx.to_undirected(nx.path_graph([6,7,8,9,10]))
c=nx.union(a,b)
ch = nx.harmonic_centrality(c)
print(ch)
print(sum(ch.values())/(nx.number_of_nodes(c)*(nx.number_of_nodes(c)-1)))
print(1. - (sum(ch.values())/(nx.number_of_nodes(c)*(nx.number_of_nodes(c)-1))))



