#!/usr/bin/env python
""" edit_puzzle.py

    This is a script to edit a KenKen puzzle.

    Use the h/j/k/l keys to move the cursor left/down/up/right.

    Hold shift to use H/J/K/L to merge the current square with the
    square left-of/below/above/right-of the cursor.
"""


# ______________________________________________________________________
# Imports

import curses
import math

import box_drawing


# ______________________________________________________________________
# Classes

# TODO: Eventually move this class into its own file.

class Puzzle(object):

    def __init__(self, size):
        self.groups = []  # Each group is a list of points.
        self.size = size

        self.x_stride = 10
        self.y_stride = 5

        self.cursor = None

    def toggle_join(self, a, b):
        """ If points a and b are already joined, this splits them.
            Otherwise, it joins their groups.
        """

        # Point lookups can fail if these are lists instead of tuples.
        a = tuple(a)
        b = tuple(b)

        if self.are_grouped(a, b):
            self.split(a, b)
        else:
            self.join(a, b)

    def find_all_paths(self, start, end, group, exclude=set()):
        """ This returns a list of paths from `start` to `end` in `group`.
            Each path is a list of points that begins with `start` and ends with
            (wait for it) `end`.
        """

        if start == end:
            return [[start]]

        pt_set = frozenset(group)  # Support fast inclusion checks.
        dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        paths = []
        for dir_ in dirs:
            next_ = tuple(start[i] + dir_[i] for i in [0, 1])
            if next_ not in group or next_ in exclude:
                continue
            new_exclude = exclude | {start}
            path_ends = self.find_all_paths(next_, end, group, new_exclude)
            for path_end in path_ends:
                paths.append([start] + path_end)
        return paths

    def split(self, a, b):
        """ This splits the group containing a and the group containing b. In
            some cases, this isn't as simple as inserting a single wall - in
            particular, when there is more than one path between a and b. In
            that case, we simply pull b out of the group.
        """

        if not self.are_grouped(a, b):
            return

        orig_group = [g for g in self.groups if a in g][0]

        if len(self.find_all_paths(a, b, orig_group)) > 1:
            orig_group.remove(b)
            return

        new_a_group = []
        new_b_group = []
        for pt in orig_group:
            path = self.find_all_paths(pt, b, orig_group)[0]
            if a in path:
                new_a_group.append(pt)
            else:
                new_b_group.append(pt)

        self.groups.remove(orig_group)
        if len(new_a_group) > 1: self.groups.append(new_a_group)
        if len(new_b_group) > 1: self.groups.append(new_b_group)

    def join(self, a, b):
        """ This joins the group including point a with the group including
            point b.
        """

        # Do this so the objects cannot later change.
        a = tuple(a)
        b = tuple(b)

        # TODO: Once I'm confident, remove debugging prints.

        dbgpr('Merging', a, 'and', b)

        a_group = [(i, g) for i, g in enumerate(self.groups) if a in g]
        b_group = [(i, g) for i, g in enumerate(self.groups) if b in g]

        dbgpr('a_group:', a_group)
        dbgpr('b_group:', b_group)

        if a_group and b_group:
            dbgpr('Clause 1')
            a_group[0][1].extend(b_group[0][1])
            del self.groups[b_group[0][0]]
        elif a_group or b_group:
            dbgpr('Clause 2')
            grp = a_group[0][1] if a_group else b_group[0][1]
            if a not in grp: grp.append(a)
            if b not in grp: grp.append(b)
        else:
            dbgpr('Clause 3')
            self.groups.append([a, b])

        # XXX
        dbgpr('At end of join, self.groups =', self.groups)

    def are_grouped(self, a, b):
        a_group = [(i, g) for i, g in enumerate(self.groups) if a in g]
        b_group = [(i, g) for i, g in enumerate(self.groups) if b in g]
        if not a_group or not b_group:
            return False
        return a_group[0][0] == b_group[0][0]

    def draw(self, stdscr, x0, y0):

        xmax = x0 + self.size * self.x_stride
        ymax = y0 + self.size * self.y_stride

        for x in range(x0, xmax + 1):
            for y in range(y0, ymax + 1):

                xval = (x - x0) / self.x_stride
                yval = (y - y0) / self.y_stride

                x1 = math.ceil (xval - 1)
                x2 = math.floor(xval)
                y1 = math.ceil (yval - 1)
                y2 = math.floor(yval)

                dirs = set()
                if (x - x0) % self.x_stride == 0:
                    if not self.are_grouped((x1, y1), (x2, y1)):
                        dirs.add('up')
                    if not self.are_grouped((x1, y2), (x2, y2)):
                        dirs.add('down')
                if (y - y0) % self.y_stride == 0:
                    if not self.are_grouped((x1, y1), (x1, y2)):
                        dirs.add('left')
                    if not self.are_grouped((x2, y1), (x2, y2)):
                        dirs.add('right')
                if x == x0:
                    dirs -= {'left'}
                if y == y0:
                    dirs -= {'up'}
                if x == xmax:
                    dirs -= {'right'}
                if y == ymax:
                    dirs -= {'down'}

                if len(dirs) > 0:
                    box_drawing.add_char(stdscr, y, x, dirs)
                    continue

                ch = ' '

                # Check to see if this is a cursor character.
                if self.cursor and x1 == x2 and y1 == y2:
                    if tuple(self.cursor) == (x1, y1):
                        ch = '.'

                stdscr.addstr(y, x, ch)


# ______________________________________________________________________
# Functions

# A debug print function.
def dbgpr(*args):
    pass


# ______________________________________________________________________
# Main

def main(stdscr):

    # XXX
    global key

    curses.curs_set(False)  # Hide the text cursor.
    stdscr.clear()

    h, w = stdscr.getmaxyx()
    # stdscr.addstr(2, 2, f'max (x, y) = ({x}, {y})')  # XXX

    puzzle = Puzzle(7)
    puzzle.cursor = [0, 0]

    puzzle_size_x = puzzle.size * puzzle.x_stride
    puzzle_size_y = puzzle.size * puzzle.y_stride

    x0 = (w - puzzle_size_x) // 2
    y0 = (h - puzzle_size_y) // 2

    movements = {'h': (-1, 0), 'j': (0, 1), 'k': (0, -1), 'l': (1, 0)}

    while True:
        puzzle.draw(stdscr, x0, y0)
        stdscr.refresh()
        key = stdscr.getkey()

        if key == 'q' or key == 'Q':
            break
        elif key in 'hjkl':
            for i in range(2):
                puzzle.cursor[i] += movements[key][i]
                puzzle.cursor[i] = puzzle.cursor[i] % puzzle.size
        elif key in 'HJKL':
            newspace = [0, 0]
            for i in range(2):
                newspace[i] = puzzle.cursor[i] + movements[key.lower()][i]
                # Don't merge cells in a wrap-around manner.
                if newspace[i] < 0 or newspace[i] == puzzle.size:
                    break
                newspace[i] %= puzzle.size
            else:  # nobreak
                puzzle.toggle_join(puzzle.cursor, newspace)
                puzzle.cursor = newspace

if __name__ == '__main__':
    curses.wrapper(main)

    print(f'key = {key}')
