""" alg_b.py

    A general backtracking algorithm.

    This can be used by things like the solver (in solver.py) and the
    number-partition-finder (in partition.py).

    The main function is named algorithm_B() after algorithm 7.2.2B in Donald
    Knuth's The Art of Computer Programming.
"""

# ______________________________________________________________________
# Public functions

def pass_(*args):
    pass

def algorithm_b(x, D, is_good, update=pass_, downdate=pass_, ell=0):
    """ This is the basic backtrack algorithm from Knuth's section 7.2.2.

        x is a list whose values will be changed as this iterates; x will be the
        list yielded when valid solutions are found.

        D is a list of lists. D[ell] is the list, in order, of all possible
        valid values for x[ell].

        is_good(x, ell) returns True when x[0], ..., x[ell] is a valid partial
        solution.

        The optional functions update() and downdate() provide callers a
        convenient way to keep track of intermediate helper data structures that
        allow is_good to operate more efficiently.
    """

    if ell == len(x):
        yield x
        return

    for d in D[ell]:
        x[ell] = d
        ell += 1
        if is_good(x, ell):
            update(x, ell)
            yield from algorithm_b(x, D, is_good, update, downdate, ell)
            downdate(x, ell)
        ell -= 1
