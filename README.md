# trendspedia-tpclustering

This is for Trendspedia project. Due to the limited number of Twitter request the system can make, it is impossible to request tweets for every wikipedia page. We have to cluster Wikipedia pages and make a request for the representative page of each cluster.


This code requires:

(1) precomputed pagerank (TODO: add the url to another repo here)

(2) precomputed page similarity (TODO: add the url to another repo here)

Users can specify minimum coverage, and the similarity threshold (see app/... for an example).


The output is clusters with hierarchical structure where the top node is the node with the highest page rank and there are edges connecting between two nodes if there are links between two pages. We can visualize the output by using this code (TODO: add url to another repository here)
