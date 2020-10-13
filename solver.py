""" solver.py

    Functionality to solve a kkpuzzler puzzle.
"""


# ______________________________________________________________________
# Imports

from collections import defaultdict
from functools import reduce
from operator import add, mul

import dbg
from alg_b import algorithm_b


# ______________________________________________________________________
# Public functions

def solve_puzzle(puzzle):
    """ This expects `puzzle` to be an instance of the Puzzle class with
        complete group and clue information.

        For now, this also assumes that a solution exists. This does not find
        multiple solutions if they exist.

        The solution is returned as a list of numbers in reading order; ie,
        corresponding to the squares (0, 0), (1, 0), (2, 0), .. <rest of row>,
        (0, 1), (1, 1), (2, 1), ... etc.

        Actually this returns a list of all found solutions. Thus, if you want,
        you could check to see if the list is empty (indicating there are no
        valid solutions), or if multiple solutions are possible.
    """

    dbg.print('SOLVER INVOKED !!!!!! GET READDDDYYYYYY')

    N = puzzle.size

    def is_soln_good(x, ell):

        # dbg.print()
        # dbg.print(f'  is_soln_good running on input:')
        # dbg.print(f'    {x[:ell]}')

        # First check that each row has unique elements.
        used_nums_per_col = defaultdict(set)
        for i, elt in enumerate(x[:ell]):
            if i % N == 0:
                used_nums_in_row = set()
            if elt in used_nums_in_row:
                # dbg.print(f'  No b/c idx {i} = {elt} is a row dup.')
                return False
            col = i % N
            if elt in used_nums_per_col[col]:
                # dbg.print(f'  No b/c idx {i} = {elt} is a col dup.')
                return False
            used_nums_per_col[col].add(elt)
            used_nums_in_row.add(elt)

        # Next check if the clues are compatible.
        for group in puzzle.groups:

            nums = [
                x[i + N * j] for i, j in group[1:]
                if i + N * j < ell
            ]

            # dbg.print(f'    Looking at the group: {group}')
            # dbg.print(f'    Got the numbers: {nums}')

            if len(nums) == 0:
                continue

            n_pts = len(group) - 1

            # Special-case handling of given squares.
            if group[0][-1] not in puzzle.op_chars:
                assert n_pts == 1
                if nums[0] != int(group[0]):
                    # dbg.print(f'  No b/c given clue {group[0]} != num {nums[0]}')
                    return False
                else:
                    continue

            clue     = group[0]
            clue_op  = clue[-1]
            clue_num = int(clue[:-1])

            if clue_op == puzzle.sub_char:
                assert n_pts == 2
                if len(nums) == 2 and abs(nums[0] - nums[1]) != clue_num:
                    return False

            if clue_op == puzzle.div_char:
                assert n_pts == 2
                nums = sorted(nums)
                if len(nums) == 2 and abs(nums[1] / nums[0]) != clue_num:
                    return False

            if clue_op == puzzle.add_char:
                sum_ = reduce(add, nums)
                if len(nums) == n_pts and sum_ != clue_num:
                    # dbg.print(f'  No b/c clue {clue} != full sum {sum_}')
                    return False
                if len(nums) < n_pts and sum_ >= clue_num:
                    # dbg.print(f'  No b/c clue {clue} <= partial sum {sum_}')
                    return False

            if clue_op == puzzle.mul_char:
                product = reduce(mul, nums)
                if len(nums) == n_pts and product != clue_num:
                    return False
                if len(nums) < n_pts and clue_num % product != 0:
                    return False

        return True

    D = [list(range(1, N + 1)) for _ in range(N * N)]
    solns = []
    for soln in algorithm_b([0] * (N * N), D, is_soln_good):
        dbg.print('I found a solution:')
        dbg.print(soln)
        solns.append(soln[:])

    return solns
