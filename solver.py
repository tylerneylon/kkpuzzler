""" solver.py

    Functionality to solve a kkpuzzler puzzle.
"""


# ______________________________________________________________________
# Imports

from collections import defaultdict
from functools import reduce
from operator import add, mul

import dbg
import partition
from alg_b import algorithm_b
from alg_P import algorithm_P


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

# ______________________________________________________________________
# Work-in-progress
#
# Everything below here is scratch code while I figure out how to set up
# a rules-based system to solve a puzzle in a human-understandable way.

# grp_options[grp_idx] = [(grp_set1, why1), (grp_set2, why2), ...]
# If a value is empty, this means we haven't evaluated it yet.
# Groups are indexed by their position in puzzle.groups.
grp_options = defaultdict(list)

# sqr_options[sqr_idx] = set_of_possible_values = (set, why).
# If a set is empty, this means we haven't evaluated it yet.
# Squares are indexed by (x, y), 0-indexed, starting at the upper-left
# corner. I decided to start at the upper-left corner for a couple reasons:
# * It's what's already used internally, based on how screen coordinates
#   typically work (for terminals).
# * It's English reading-order, which I think many people will find more
#   intuitive as I plan to express it as, eg, square C3, similar to a
#   spreadsheet.
sqr_options = defaultdict(list)

# This is a list of deductions of the form (str, why).
soln_hist = []

# In each of the above, a `why` object has the form:
#     [RULE_NAME, hist_idx1, hist_idx2, ...]
# where RULE_NAME is a string and the subsequent history indexes point
# into soln_hist to tell us which previous deductions were used.

# Our soln_hist has two parts to it: a prefix that we consider to be "good
# enough so far," and a suffix which we may prune as we proceed.
# The "good enough so far" prefix is exactly soln_hist[:good_soln].
good_soln = 0

# This is a list of puzzle.size^2 values that begin as all '?' strings, and that
# we'll work to turn into numeric values with the puzzle's solution.
full_soln = []

def elt(singleton):
    """ Return the value of the single element in the set `singleton`. """
    assert type(singleton) == set
    assert len(singleton) == 1
    return next(iter(singleton))

def is_multisubset(a, b):
    """ Return True when list a is a subset of list b, considering both as
        multisets.
    """
    c = b[:]
    for a_elt in a:
        if a_elt not in c:
            return False
        c.remove(a_elt)
    return True

def multiset_sub(big, small):
    """ Return `big` - `small`, seen as multisets. """
    assert is_multisubset(small, big)
    delta = big[:]
    for elt in small:
        delta.remove(elt)
    return delta

def get_line_limited_info(puzzle, coord, val, excl_grp=None):
    """ This looks at the line given by pt[coord] == val.
        This returns knowns_by_sqr, caught_in_line.
        `knowns_by_sqr` is a list of items of these three possible values:
        * int  This denotes a square with an exactly-known value.
        * '?'  This denotes a square with unknown value.
        * set  This denotes a square with a known set of possible values.
               This is the intersection given by grp_options and sqr_options.
        * list This denotes an all-in-line group. It will have the form
               [grp_len, grp_options].
        `caught_in_line` is the set of numbers such that we either know exactly
        which square in this line has that value, or we know exactly which group
        in this line has that value.

        If a group (an element of puzzle.groups) is provided in excl_grp, then
        we pretend that nothing is known about that given group.
    """

    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    # XXX
    do_debug_print = False

    if do_debug_print:
        dbg.print(f'get_line_limited_info(puzzle, {coord}, {val})')

    lst_pt = [0, 0]
    lst_pt[coord] = val

    knowns_by_sqr = []
    caught_in_line = set()

    c2 = 1 - coord
    for v2 in range(puzzle.size):

        lst_pt[c2] = v2
        pt = tuple(lst_pt)

        # Are we skipping this square?
        if excl_grp and pt in excl_grp:
            continue

        # Have we solved this square?

        if len(sqr_options[pt]) > 0 and len(sqr_options[pt][0]) == 1:
            num = elt(sqr_options[pt][0])
            knowns_by_sqr.append(num)
            caught_in_line.add(num)
            continue

        # Is this part of an all-in-line group?

        sqr_choices = set(range(1, puzzle.size + 1))

        grp = puzzle.get_group_at_point(pt)
        i = puzzle.groups.index(grp)
        if all(p[coord] == val for p in grp[1:]):
            if len(grp_options[i]) == 1:
                nums = set(grp_options[i][0][0])
                knowns_by_sqr.append([len(grp) - 1, nums])
                caught_in_line |= nums
                continue
            elif len(grp_options[i]) > 1:
                sqr_choices = set.union(*[
                    set(option[0])
                    for option in grp_options[i]
                ])
        else:

            # We may be able to narrow down sqr_choices by starting with all the
            # group options (even if it is not all in this line).

            sqr_choices = set.union(*[
                set(option[0])
                for option in grp_options[i]
            ])

        # Check to see how much info we gain from sqr_options.

        if len(sqr_options[pt]) > 0 and len(sqr_options[pt][0]) > 1:
            sqr_choices &= sqr_options[pt][0]

        if len(sqr_choices) < puzzle.size:
            knowns_by_sqr.append(sqr_choices)
        else:
            knowns_by_sqr.append('?')

    if do_debug_print:
        dbg.print(f'  will return {knowns_by_sqr}, {caught_in_line}')

    return knowns_by_sqr, caught_in_line

def check_for_line_elims(puzzle):
    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    did_make_progress = False

    for val in range(puzzle.size):
        for coord in [0, 1]:
            knowns_by_sqr, caught_in_line = get_line_limited_info(
                    puzzle,
                    coord,
                    val
            )
            if len(caught_in_line) != puzzle.size - 1:
                continue

            # At this point, we have found a new square value.

            set_idx = [
                    i
                    for i, sqr in enumerate(knowns_by_sqr)
                    if type(sqr) is set
            ]

            if knowns_by_sqr.count('?') == 1:
                i = knowns_by_sqr.index('?')
            elif len(set_idx) == 1:
                i = set_idx[0]
            else:
                assert False  # Expected only one unknown square.

            pt = (val, i) if coord == 0 else (i, val)
            sqr_val = elt(set(range(1, puzzle.size + 1)) - caught_in_line)
            why = ('line_elim', [])  # TODO: Account for history here.
            sqr_options[pt] = ({sqr_val}, why)
            line_name = 'col' if coord == 0 else 'row'
            step = f'{pt_name(pt)}={sqr_val} by {line_name} elimination.'
            soln_hist.append(step)
            full_soln[pt[0] + puzzle.size * pt[1]] = sqr_val
            dbg.print(step)
            did_make_progress = True

    # XXX
    # dbg.print(f'check_for_line_elims() will return {did_make_progress}')
    return did_make_progress

# XXX I'm not actually calling this function right now.
#     Decide if I'll either finish-and-integrate this, or drop it.
#     If I want to finish it, I'd like to have at least one test case
#     where it's clearly useful.
def check_and_remove_bad_grp_options(puzzle):
    # XXX Do I actually use all of these?
    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    did_make_progress = False  # XXX Do I actually need this?

    # XXX temp; for reference
    if False:
        for val in range(puzzle.size):
            for coord in [0, 1]:
                knowns_by_sqr, caught_in_line = get_line_limited_info(
                        puzzle,
                        coord,
                        val
                )

    # TODO HERE:
    # Question: How can I skip groups that we've already solved?
    # For example, at my current point in f.kk, we ought to skip
    # group 0 here.

    # For each group, look for options that can't actually fit in.
    for i, grp in enumerate(puzzle.groups):
        dbg.print()
        dbg.print(f'Thinking about group {i} with clue {grp[0]}.')
        options = grp_options[i]
        for option in options:
            # Enumerate over all possible ways of filling in this group.
            nums = option[0]
            for sqrs in algorithm_P(grp[1:]):
                # Visit the mapping sqrs[i] -> nums[i].
                dbg.print('Placing', end='')
                for sqr, n in zip(sqrs, nums):
                    dbg.print(f' {n} @ {sqr}', end='')
                dbg.print()
    # XXX TODO
    return False

def check_for_single_grp_option(puzzle):
    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    part_fn_map = {
            puzzle.add_char: partition.get_add_partitions,
            puzzle.sub_char: partition.get_sub_partitions,
            puzzle.mul_char: partition.get_mul_partitions,
            puzzle.div_char: partition.get_div_partitions
    }

    did_make_progress = False

    for i, grp in enumerate(puzzle.groups):

        if len(grp_options[i]) == 1:
            # We already have full group info here; skip.
            continue

        clue = grp[0]

        if clue == '':
            dbg.print('WARNING: Soln request on a puzzle w an empty clue!!')
            return

        op_char = clue[-1]
        if op_char not in puzzle.op_chars:
            # This happens for single-box groups with given values.
            continue
        num_sq = len(grp) - 1
        group_w = len({pt[0] for pt in grp[1:]})
        group_h = len({pt[1] for pt in grp[1:]})
        # Note that `max_repeat` does not fully capture the constraints of a
        # shape. For example, a shape might support 3 copies of one number, but
        # the next-most-frequent number may only be allowed 2 copies.
        # It may be fun to explore the mathematical properties of carrying
        # capacities of group shapes, as simple as it first appears.
        max_repeat = min(group_w, group_h)
        # TODO: There is duplicate work here. What we're doing here should
        #       already be done when we initially populate grp_options. And then
        #       we ought to be using the list in grp_options rather than
        #       re-calculating this here.
        parts = part_fn_map[op_char](
                puzzle.size,
                int(clue[:-1]),
                num_sq,
                max_repeat
        )

        # For groups in a single line, check for compatibility within the line.
        if group_w == 1 or group_h == 1:

            coord = 0 if group_w == 1 else 1
            val = grp[1][coord]

            knowns_by_sqr, caught_in_line = get_line_limited_info(
                    puzzle,
                    coord,
                    val,
                    excl_grp = grp  # So that caught_in_line excludes this grp.
            )

            # XXX rest of this block
            start_num_parts = len(parts)

            parts = [
                    part
                    for part in parts
                    if not (set(part) & caught_in_line)
            ]

            end_num_parts = len(parts)

            # XXX
            if end_num_parts == 0:  # Can't happen if the puzzle is solvable.
                import ipdb
                ipdb.set_trace()

            if end_num_parts < start_num_parts:
                dbg.print('*' * 70)
                dbg.print(f'I have the reduced partition set (clue={clue}):')
                dbg.print(parts)

        # TODO: Intersect parts with the current group options.
        #       (This won't be needed if we simply use grp_options as our source
        #       for `parts`.)

        # TODO Later: Try all layouts for each partition to see if it can
        #             possibly be compatible with each line that it's in.

        if not (len(parts) == 1 and len(grp_options[i]) != 1):
            continue

        # XXX
        k = len(grp_options[i])
        dbg.print(f'I think I found smth new b/c len(grp_options[i]) = {k}')
        dbg.print(f'Specifically, grp_options[i] = {grp_options[i]}')

        numlist = parts[0]
        why = ('single_grp_opt', [])
        grp_options[i] = [(numlist, why)]
        clue_pt = puzzle.get_clue_point(grp)
        step = f'Group @ {pt_name(clue_pt)}({grp[0]}) is {numlist}'
        soln_hist.append(step)
        dbg.print(step)
        did_make_progress = True

    # dbg.print(f'check_for_single_grp_option() will return {did_make_progress}')
    return did_make_progress

def check_for_grp_completion(puzzle):
    """ Look for groups where we've filled in all the squares except for one.
        In some cases, we can uniquely determine the last square, but (for the -
        or / operators), not always.
    """
    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    part_fn_map = {
            puzzle.add_char: partition.get_add_partitions,
            puzzle.sub_char: partition.get_sub_partitions,
            puzzle.mul_char: partition.get_mul_partitions,
            puzzle.div_char: partition.get_div_partitions
    }

    did_make_progress = False

    for i, grp in enumerate(puzzle.groups):

        grp_size = len(grp) - 1  # -1 for the clue

        # TODO: Needed?
        if grp_size < 1:
            continue

        # Check to see if we know all squares but one in this group.
        known_in_grp = []
        unknown_pt = None
        for pt in grp[1:]:
            sqr_set = sqr_options[pt][0] if sqr_options[pt] else set()
            if len(sqr_set) == 1:
                known_in_grp.append(elt(sqr_set))
            else:
                unknown_pt = pt

        if len(known_in_grp) != grp_size - 1:
            continue

        # The square might yet be unknown. Eg, the clue is 1- and the val is 3.
        # Get the possible partitions and use those.

        clue = grp[0]

        op_char = clue[-1]
        if op_char not in puzzle.op_chars:
            continue
        num_sq = len(grp) - 1
        group_w = len({pt[0] for pt in grp[1:]})
        group_h = len({pt[1] for pt in grp[1:]})
        max_repeat = min(group_w, group_h)
        parts = part_fn_map[op_char](
                puzzle.size,
                int(clue[:-1]),
                num_sq,
                max_repeat
        )

        compatible_parts = [
                part
                for part in parts
                if is_multisubset(known_in_grp, part)
        ]

        assert len(compatible_parts) > 0
        if len(compatible_parts) != 1:
            continue  # This is the case where we don't know the sqr yet.

        delta = multiset_sub(compatible_parts[0], known_in_grp)
        assert len(delta) == 1
        sqr_val = delta[0]
        why = ('grp_completion', [])  # TODO: Account for history.
        sqr_options[unknown_pt] = ({sqr_val}, why)
        step = f'{pt_name(unknown_pt)}={sqr_val} by group completion.'
        soln_hist.append(step)
        full_soln[unknown_pt[0] + puzzle.size * unknown_pt[1]] = sqr_val
        dbg.print(step)
        did_make_progress = True

    return did_make_progress

def check_for_one_place_left(puzzle):

    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    did_make_progress = False

    for val in range(puzzle.size):
        for coord in [0, 1]:
            knowns_by_sqr, caught_in_line = get_line_limited_info(
                    puzzle,
                    coord,
                    val
            )

            # For each num, check to see how many spaces it could live in.
            for num in range(1, puzzle.size + 1):
                num_homes = 0
                home_val = -1
                is_solved = False
                for i, sqr in enumerate(knowns_by_sqr):
                    if sqr == '?':
                        num_homes += 1
                        home_val = i
                    elif type(sqr) is list:  # An in-line group.
                        if num in sqr[1]:
                            num_homes += 1
                            home_val = i
                    elif type(sqr) is set:  # A partial-info square.
                        if num in sqr:
                            num_homes += 1
                            home_val = i
                    elif type(sqr) is int:  # A solved square.
                        if sqr == num:
                            is_solved = True
                            break
                    else:
                        # We should recognize every square value type.
                        assert False
                    if num_homes > 1:
                        break
                if is_solved:
                    continue
                if num_homes == 1:
                    pt = (val, home_val) if coord == 0 else (home_val, val)
                    why = ('one_place_left', [])  # TODO: Account for history.
                    sqr_options[pt] = ({num}, why)
                    line_name = 'col' if coord == 0 else 'row'
                    step = f'''
                        {pt_name(pt)}={num} by only-place-left in {line_name}.
                    '''.strip()
                    soln_hist.append(step)
                    full_soln[pt[0] + puzzle.size * pt[1]] = num
                    dbg.print(step)
                    did_make_progress = True

    return did_make_progress

def pt_name(pt):
    xname = chr(ord('a') + pt[0])
    return f'{xname}{pt[1] + 1}'

def pretty_print_grp_options(puzzle):
    global grp_options
    for i, grp in enumerate(puzzle.groups):
        clue_pt = puzzle.get_clue_point(grp)
        dbg.print(f'{grp[0]:4s} @ {clue_pt}: ', end='')
        dbg.print(*[x[0] for x in grp_options[i]])

# XXX
# This next function is a work-in-progress as I figure out how to set up a
# rules-based puzzle-solving system.
def print_human_friendly_soln(puzzle):
    global grp_options, sqr_options, soln_hist, good_soln, full_soln

    grp_options = defaultdict(list)
    sqr_options = defaultdict(list)
    soln_hist = []
    good_soln = 0
    full_soln = ['?'] * (puzzle.size ** 2)

    # We can record that a square has a known value by giving it a singleton set
    # in sqr_options.

    # 1. Find given squares.

    for x in range(puzzle.size):
        for y in range(puzzle.size):
            pt = (x, y)
            grp = puzzle.get_group_at_point(pt)
            if len(grp) == 2:
                val = int(grp[0])
                why = ('given', [])
                sqr_options[pt] = ({val}, why)
                soln_hist.append(f'Given: {pt_name(pt)}={val}')
                full_soln[pt[0] + puzzle.size * pt[1]] = val
                good_soln += 1
                dbg.print(soln_hist[-1])

    # 2. Set up initial grp_options.

    part_fn_map = {
            puzzle.add_char: partition.get_add_partitions,
            puzzle.sub_char: partition.get_sub_partitions,
            puzzle.mul_char: partition.get_mul_partitions,
            puzzle.div_char: partition.get_div_partitions
    }

    for i, grp in enumerate(puzzle.groups):

        clue = grp[0]

        if clue == '':
            dbg.print('WARNING: Soln req on a puzzle w an empty clue!!')
            # TODO: Ensure we don't crash on a bad puzzle.

        op_char = clue[-1]
        if op_char not in puzzle.op_chars:
            continue
        num_sq = len(grp) - 1
        group_w = len({pt[0] for pt in grp[1:]})
        group_h = len({pt[1] for pt in grp[1:]})
        max_repeat = min(group_w, group_h)
        parts = part_fn_map[op_char](
                puzzle.size,
                int(clue[:-1]),
                num_sq,
                max_repeat
        )

        grp_options[i] = [
                (sorted(part), 'listing all group options')
                for part in parts
        ]

    dbg.print('sqr_options:')
    dbg.print(sqr_options)
    dbg.print('grp_options:')
    pretty_print_grp_options(puzzle)

    # XXX
    i = 1

    did_make_progress = True
    while did_make_progress:

        dbg.print(f'\nStart of iteration {i}.\n')

        did_make_progress = False
        did_make_progress |= check_for_line_elims(puzzle)
        # TODO: Drop check_for_single_grp_option().
        #       I believe it's made obsolete by step 2 above.
        did_make_progress |= check_for_single_grp_option(puzzle)
        did_make_progress |= check_for_grp_completion(puzzle)
        did_make_progress |= check_and_remove_bad_grp_options(puzzle)

        # I consider check-for-one-place-left to be a slightly trickier
        # rule, so we only apply it when we get stuck with the simpler rules.
        if not did_make_progress:
            did_make_progress |= check_for_one_place_left(puzzle)

        # TODO:      Add a method which eliminates known-bad grp_options. It
        #            will try out all possible placements of the options for
        #            each group. Some groups will have all their possible
        #            placements conflicting with the data we get from
        #            get_line_limited_info() in terms of caught
        #            (-in-other-group) numbers. We can eliminate those group
        #            options. Test this on the file f.kk.
        #
        #            Along with this, it would be nice to start formally
        #            deciding the difficulty rating of the various rules being
        #            used. The idea here is to help understand the difficulty of
        #            a puzzle by understanding the most-difficult rule that had
        #            to be used. In some cases, I may feel as if different
        #            applications of the same Python method may qualify as
        #            different difficulty settings.
        #
        #            Added note: I am doing this work in the function
        #            check_and_remove_bad_grp_options(), called above.

        dmp = did_make_progress
        dbg.print(f'Ending iteration {i}; did_make_progress = {dmp}.')

        i += 1

    dbg.print('\n' + '_' * 30)

    dbg.print('\nFinal row-based knowledge is:')
    for val in range(puzzle.size):
        knowns_by_sqr, caught_in_line = get_line_limited_info(
                puzzle,
                1,  # coord
                val
        )
        prefix = f'Row {val}: {knowns_by_sqr}'
        dbg.print(f'{prefix:60s} Caught values: {caught_in_line}')

    dbg.print('\nFinal grp_options are as follows:')
    pretty_print_grp_options(puzzle)

    puzzle.add_solution(full_soln)
