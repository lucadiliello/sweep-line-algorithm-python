import networkx as nx
from matplotlib import *
from pylab import *
import random
import itertools
from time import time
from SweepLineAlgorithm.geometry import Graph


def generate_circuit(n_nodes, n_edges, ranges=(0,50)):
    if n_edges > n_nodes * (n_nodes-1)/2:
        # this graph cannot exists
        return None

    nodes = [(random.uniform(*ranges), random.uniform(*ranges)) for i in range(n_nodes)]

    all_edges = list(itertools.combinations(range(n_nodes), 2))
    edges = []
    for i in range(n_edges):
        j = random.randint(0,len(all_edges)-1)
        edges.append(all_edges[j])
        del all_edges[j]

    return Graph(nodes, edges)

if __name__ == "__main__":
    for i in range(5):
        G = generate_circuit(15,30)
        print G.intersection_number()

    start = time()
    print "Intersections:", G.intersection_number()
    print "Algorithm required: %d seconds" % (time()-start)
    G.plot()
