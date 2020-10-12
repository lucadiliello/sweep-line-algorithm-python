# sweep-line-algorithm-python

A Python implementation of the Sweep Line Algorithm.
The algorithm works fine if no segment is perfectly vertical, otherwise the number of intersections found could be different from the real result. However, in most cases it seems to work fine even with vertical segments.

It uses a custom version of a PriorityQueue (to store the events) and a custom version of a TreeSet (to store the state segments).

Launch:
```
python2 example.py
```
and enjoy!
