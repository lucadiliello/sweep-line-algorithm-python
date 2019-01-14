import networkx as nx
from matplotlib import *
from pylab import *
import random
import itertools
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

    # generating a random graph
    G = generate_circuit(5,8)

    # print number of crossing edges and the total length of the edges
    print "Intersections:", G.intersection_number(), "Total edges length:", G.edges_total_length()
    # draw the graph
    G.plot()

    # moving the first node to x = 100
    G.nodes[0].x = 100

    # print again the number of crossing edges and the total length of the edges
    print "Intersections:", G.intersection_number(), "Total edges length:", G.edges_total_length()
    # draw the graph
    G.plot()
