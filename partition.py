""" partition.py

    Functions to help determine which values can be valid in a given puzzle.
"""


# ______________________________________________________________________
# Imports

from collections import Counter
from functools import reduce
from operator import add, mul

from alg_b import algorithm_b


# ______________________________________________________________________
# Internal functions

def get_addmul_partitions(hi,clue_num, num_sq, max_repeat, op):
    """ Return a list of lists, each sublist containing num_sq elements with
        their sum or product (based on op == add or op == mul) being equal to
        clue_num. The sublists also meet the requirement that the most common
        element occurs at most max_repeat times.
    """
    def is_good(x, ell):

        if sorted(x[:ell]) != x[:ell]:
            return False

        repeat = Counter(x[:ell]).most_common(1)[0][1]
        if repeat > max_repeat:
            return False

        val = reduce(op, x[:ell])

        if ell == num_sq:
            return val == clue_num

        if op == add:
            return val < clue_num
        else:
            return val <= clue_num

    x = [0] * num_sq
    D = [list(range(1, hi + 1))] * num_sq
    return [x[:] for x in algorithm_b(x, D, is_good)]


# ______________________________________________________________________
# Public functions

def get_add_partitions(hi, clue_num, num_sq, max_repeat):
    return get_addmul_partitions(hi, clue_num, num_sq, max_repeat, add)

def get_mul_partitions(hi, clue_num, num_sq, max_repeat):
    return get_addmul_partitions(hi, clue_num, num_sq, max_repeat, mul)

def get_sub_partitions(hi, clue_num, num_sq=None, max_repeat=None):
    return [
            [a, a + clue_num]
            for a in range(1, hi - clue_num + 1)
    ]

def get_div_partitions(hi, clue_num, num_sq=None, max_repeat=None):
    return [
            [a, a * clue_num]
            for a in range(1, hi // clue_num + 1)
    ]
