import math
from decimal import *
from treeset import TreeSet
from priorityqueue import PriorityQueue
import networkx as nx
from matplotlib import *
from pylab import *
import random
import itertools

quantizer = Decimal('10') ** -15

# A node of the graph
class Node(object):

    def __init__(self, id, x, y):
        self.x = Decimal(x)#.quantize(quantizer)
        self.y = Decimal(y)#.quantize(quantizer)
        self.id = id

    def __str__(self):
        return "(id:{0}, coord:({1},{2}))".format(self.id, self.x, self.y)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.x.quantize(quantizer), self.y.quantize(quantizer)))

    def __lt__(self, other):
        return self.x < other.x or self.x == other.x and self.y < other.y

    def coord(self):
        return (self.x, self.y)

# An end of a segment. It points to a node, from which it receives the coordinates
class Point(object):
    def __init__(self, node=None, status=None, segment=None):
        self.node = node
        self.status = status # left, right, int
        self.segment = segment

    def __update__(self, other):
        self.node = other.node
        self.status = other.status
        self.segment = other.segment

    def __str__(self):
        return "(node:{0}, stat:{1})".format(self.node, self.status)

    def __hash__(self):
        return hash(self.node)

    def __eq__(self, other):
        return self.node is other.node

    def __lt__(self, other):
        if self.node.x < other.node.x:
            return True
        elif self.node.x > other.node.x:
            return False
        elif self.node.y < self.node.y:
            return True
        elif self.node.y > other.node.y:
            return False
        elif self.status == "int":
            return True
        elif self.status == "left":
            return other.status == "left"
        else:
            return other.status != "int"

    def __gt__(self, other):
        return not self.__lt__(other)

# A line between two points
class Segment(object):
    def __init__(self, p, q, graph=None):
        # the current node of
        self.graph = graph
        # p is the left-most point of each segment
        if p.node < q.node:
            self.p = p
            self.q = q
        else:
            self.p = q
            self.q = p

        self.p.status = "left"
        self.q.status = "right"
        self.p.segment = self.q.segment = self
        self.params = {}
        self.refresh()

    def set_p_node(self, n):
        self.p.node = n
        self.refresh()

    def set_q_node(self, n):
        self.q.node = n
        self.refresh()

    def actual_y(self):
        if self.graph.current == self.p:
            return self.p.node.y
        elif self.graph.current == self.q:
            return self.q.node.y
        else:
            if self.params['m']:
                return self.params['m'] * self.graph.current.node.x + self.params['q']
            else:
                return self.p.node.y

    def refresh(self):
        self.params['m'] = self.get_m()
        self.params['q'] = self.get_q()

    def get_m(self):
        if self.p.node.x.quantize(quantizer) != self.q.node.x.quantize(quantizer):
            return (self.p.node.y - self.q.node.y) / (self.p.node.x - self.q.node.x)
        else:
            return None

    def get_q(self):
        if self.params['m']:
            return self.p.node.y - self.params['m'] * self.p.node.x
        else:
            return None

    # res > 0 se il segment e' orizzontale, verticale o obliquo.
    # 0 < res < 1 piu' ci si avvicina ai casi opposti (22.5deg, 67.5deg, ...)
    def squareness(self):
        m = self.get_m()
        m = math.pi/2 if m is None else math.atan(m)
        return math.sin(m * 4) ** 4

    def __str__(self):
        return "({0},{1})".format(self.p.node.id, self.q.node.id)

    def __lt__(self, other):
        if self == other:
            return False
        if self.actual_y() == other.actual_y():
            return self.params['m'] < other.params['m']
        else:
            return self.actual_y() < other.actual_y()

    def __gt__(self, other):
        return not self.__lt__(other) and not self == other

    def __len__(self):
        return math.sqrt((self.p.node.x - self.q.node.x) ** 2 + (self.p.node.y - self.q.node.y) ** 2)

    def __eq__(self, other):
        if not other:
            return False
        return self.p == other.p and self.q == other.q

    def __adj__(self, other):
        return self.p == other.p or self.p == other.q \
            or self.q == other.p or self.q == other.q

    def orientation(self, p, q, r):
        val = (q.node.y - p.node.y) * (r.node.x - q.node.x) - (q.node.x - p.node.x) * (r.node.y - q.node.y)
        return 0 if abs(val) < 10**(-9) else (1 if val > 0 else -1)

    def on_segment(self, p, q, r):
        return (min(p.node.x, q.node.x) <= r.node.x) and (r.node.x <= max(p.node.x, q.node.x)) and \
            (min(p.node.y, q.node.y) <= r.node.y) and (r.node.y <= max(p.node.y, q.node.y))

    def intersect(self, other):
        if self.__adj__(other):
            return False

        o1 = self.orientation(self.p, self.q, other.p)
        o2 = self.orientation(self.p, self.q, other.q)
        o3 = self.orientation(other.p, other.q, self.p)
        o4 = self.orientation(other.p, other.q, self.q)

        if (o1 != o2) and (o3 != o4):
            return True

        return (o1 == 0) and self.on_segment(self.p, self.q, other.p) \
            or (o2 == 0) and self.on_segment(self.p, self.q, other.q) \
            or (o3 == 0) and self.on_segment(other.p, other.q, self.p) \
            or (o4 == 0) and self.on_segment(other.p, other.q, self.q)


    def intersection_point(self, other):
        # Segment AB represented as a1x + b1y = c1
        a1 = self.q.node.y - self.p.node.y
        b1 = self.p.node.x - self.q.node.x
        c1 = self.p.node.y * b1 + self.p.node.x * a1

        # Segment CD represented as a2x + b2y = c2
        a2 = other.q.node.y - other.p.node.y
        b2 = other.p.node.x - other.q.node.x
        c2 = other.p.node.y * b2 + other.p.node.x * a2

        determinant = a1 * b2 - a2 * b1

        if determinant:
            x = (b2 * c1 - b1 * c2) / determinant
            y = (a1 * c2 - a2 * c1) / determinant
            res = Point(self.graph.get_node(x,y), "int", (self, other))
            return res
        return None

class SweepPlaneException(Exception):
    def __init__(self, message):
        super(SweepPlaneException, self).__init__(message)
        self.msg = message

    def __str__(self):
        if self.msg:
            return self.msg
        return "Generic error in the sweep line algorithm"

class Graph(object):
    def __init__(self, nodes=[], edges=[]):
        self.nodes = [Node(i, *nodes[i]) for i in range(len(nodes))]
        self.original_n_nodes = len(self.nodes)
        self.current = Point()
        self.edges = edges
        self.segments = [Segment(Point(self.nodes[e[0]]), \
            Point(self.nodes[e[1]]), self) for e in self.edges]

    def get_node(self, x, y):
        target = Node(-1, x, y)
        for n in self.nodes:
            if hash(n) == hash(target):
                return n
        target.id = len(self.nodes)
        self.nodes.append(target)
        return target

    def intersection_number(self):
        if len(self.segments) < 50:
            # brute force faster on small graphs
            return self.brute_force()
            # return self.sweep_line_algorithm()
        else: return self.sweep_line_algorithm()

    def brute_force(self):
        #print [str(x) for x in segments]
        res = 0
        for i in range(len(self.segments)-1):
            for j in range(i+1, len(self.segments)):
                if self.segments[i].intersect(self.segments[j]):
                    res += 1
        return res

    def sweep_line_algorithm(self):
            self.current = Point()

            pointsPQ = PriorityQueue()
            tree = TreeSet()

            pointsPQ.pushAll([seg.p for seg in self.segments])
            pointsPQ.pushAll([seg.q for seg in self.segments])

            res = 0
            #print [str(x) for x in pointsPQ]

            while not pointsPQ.isEmpty():

                self.current.__update__(pointsPQ.pop())

                #print "Round", current

                if self.current.status == 'left':
                    #print "Adding", self.current.segment
                    low, high = tree.add_high_low(self.current.segment)

                    low = tree.lower(self.current.segment)
                    high = tree.higher(self.current.segment)
                    #print "Actual:", self.current.segment
                    #print "Low:", low, self.current.segment.intersect(low) if low else False
                    #print "High:", high, self.current.segment.intersect(high) if high else False

                    if low:
                        if self.current.segment.intersect(low):
                            a = self.current.segment.intersection_point(low)
                            #print "Adding a:", a, self.current.segment, low
                            pointsPQ.push(a)

                    if high:
                        if self.current.segment.intersect(high):
                            a = self.current.segment.intersection_point(high)
                            #print "Adding 2:", a, self.current.segment, high
                            pointsPQ.push(a)

                elif self.current.status == "right":
                    low = tree.lower(self.current.segment)
                    high = tree.higher(self.current.segment)

                    if low and high:
                        if low.intersect(high):
                            a = low.intersection_point(high)
                            #print "Adding 3:", a, low, high
                            pointsPQ.push(a)

                    tree.remove(self.current.segment)
                    #print "Removing", self.current.segment

                elif self.current.status == "int":
                    # exchange the position in tree of the two segments intersecting in current
                    s1, s2 = self.current.segment
                    #print "Between, swapping:", str(s1), str(s2)

                    tree.swap(s1, s2)

                    #print "After swap:", s1, s2, s1 is tree.lower(s2), s2 is tree.lower(s1)
                    #print "Modifying segments starts"
                    old_s1 = s1.p.node
                    old_s2 = s2.p.node

                    s1.set_p_node(self.current.node)
                    s2.set_p_node(self.current.node)

                    #print "Tree after modification:", [str(x) for x in tree]

                    # s1
                    if s1 is tree.lower(s2):
                        #print "... s1, s2, ..."

                        low = tree.lower(s1)
                        #print "s1:", s1, "low:", low, s1.intersect(low) if low else False

                        if low is not None:
                            if s1.intersect(low):
                                pointsPQ.push(s1.intersection_point(low))

                        high = tree.higher(s2)
                        #print "s2:", s2, "high:", high, s2.intersect(high) if high else False

                        if high is not None:
                            if s2.intersect(high):
                                pointsPQ.push(s2.intersection_point(high))

                    elif s2 is tree.lower(s1):
                        #print "... s2, s1, ..."

                        high = tree.higher(s1)
                        #print "s1:", s1, "high:", high, s1.intersect(high) if high else False

                        if high is not None:
                            if s1.intersect(high):
                                pointsPQ.push(s1.intersection_point(high))

                        low = tree.lower(s2)
                        #print "s2:", s2, "low:", low, s2.intersect(low) if low else False

                        if low is not None:
                            if s2.intersect(low):
                                pointsPQ.push(s2.intersection_point(low))

                    else:
                        print "Error" #raise SweepPlaneException("Intersection point error!")
                    res += 1

                    s1.set_p_node(old_s1)
                    s2.set_p_node(old_s2)

                else:
                    print "Error 2" #raise SweepPlaneException("Node without status!")
                #print "Tree", [str(x) for x in tree]
                #print ""
            self.nodes = self.nodes[:self.original_n_nodes]
            return res

    def edges_total_length(self):
        return sum([len(s) for s in self.segments])

    def edges_squareness(self):
        return sum([s.squareness() for s in self.segments])

    def plot(self):
        res = nx.Graph()

        for i in range(len(self.nodes)):
            res.add_node(i, pos=self.nodes[i].coord())

        for e in self.segments:
            res.add_edge(e.p.node.id, e.q.node.id)

        pos = nx.get_node_attributes(res, 'pos')
        nx.draw(res, pos, with_labels = 'True')
        ioff()
        show()
