#!/usr/bin/env python
""" puzzle.py

    The Puzzle class encapsulates a puzzle instance.
"""


# ______________________________________________________________________
# Imports

import curses
import json
import math

import drawing


# ______________________________________________________________________
# Globals

# These are curses color indexes.
GROUP_HIGHLIGHT = 2
BACKGROUND      = 3


# ______________________________________________________________________
# Main class

class Puzzle(object):

    # __________________________________________________________________
    # Constructor

    def __init__(self, size=4):
        self.groups = []  # Each group is a list of points.
        self.size = size

        self.x_stride = 10
        self.y_stride = 5

        # I am considering allowing self.cursor == None, which would indicate
        # we're in a display-only mode. This might be interesting for simply
        # viewing a puzzle (like `cat FILE`), or printing a puzzle.
        self.cursor = [0, 0]

        # The format here is (index, foreground, background).
        curses.init_pair(GROUP_HIGHLIGHT, 246, 236)
        curses.init_pair(BACKGROUND, 7, 16)

    # __________________________________________________________________
    # Methods to modify the puzzle

    # I'm calling this "reset" rather than "set" because it involves potentially
    # throwing away quite a bit of data.
    def reset_size(self, new_size):
        if new_size < self.size:
            self.groups = []
        self.size = new_size
        self.cursor = [0, 0]

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

    def set_clue_at_cursor(self, clue):
        pass  # XXX TODO

    # __________________________________________________________________
    # Utility methods

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

    def are_grouped(self, a, b):
        a_group = [(i, g) for i, g in enumerate(self.groups) if a in g]
        b_group = [(i, g) for i, g in enumerate(self.groups) if b in g]
        if not a_group or not b_group:
            return False
        return a_group[0][0] == b_group[0][0]

    def jump_to_clue_subline(self, stdscr):
        """ Jump the cursor to the clue-holding square for the current group,
            and return (y, x1, x2) for the clue text area of the cursor's (clue)
            square. The valid x range is [x1, x2), excluding x2. """

        # This only makes sense if this puzzle has been drawn (otherwise we
        # won't have x0, y0 coordinates).
        assert 'x0' in self.__dict__

        # Find the first square of the current group, in English reading order.
        # We'll jump the cursor to that square.
        groups = [g for g in self.groups if tuple(self.cursor) in g]
        if len(groups) > 0:
            group = groups[0]
            first_sq = sorted(
                    group,
                    key=lambda pt: self.size * pt[1] + pt[0]
            )[0]
            self.cursor = list(first_sq)
            self.draw(stdscr, self.x0, self.y0)
            stdscr.refresh()

        y  = self.y0 + self.cursor[1] * self.y_stride + 1
        x1 = self.x0 + self.cursor[0] * self.x_stride + 1
        x2 = x1 + self.x_stride - 1

        return (y, x1, x2)

    # __________________________________________________________________
    # Display and visual editing methods

    def edit_clue(self, stdscr):
        """ Let the user modify the clue for the group containing the
            cursor.
        """
        assert self.cursor

        # A `subline` is (y, x1, x2).
        subline = self.jump_to_clue_subline(stdscr)
        clue = drawing.edit_subline(stdscr, subline)
        if clue is None:
            return
        # TODO: Check if clue strings are valid. If not, we can highlight
        #       them in red so users can correct them.
        self.set_clue_at_cursor(clue)

    def draw(self, stdscr, x0, y0):

        # TODO Call this only once.
        stdscr.bkgd(' ', curses.color_pair(BACKGROUND))

        current_group = []
        for group in self.groups:
            if tuple(self.cursor) in group:
                current_group = group

        self.x0 = x0
        self.y0 = y0

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
                    drawing.add_char(stdscr, y, x, dirs)
                    continue

                ch = ' '
                attr = curses.color_pair(0)

                # Check to see if this is a cursor character.
                if self.cursor and x1 == x2 and y1 == y2:
                    if tuple(self.cursor) == (x1, y1):
                        ch = '.'
                        attr = curses.color_pair(GROUP_HIGHLIGHT)
                    if (x1, y1) in current_group:
                        attr = curses.color_pair(GROUP_HIGHLIGHT)

                stdscr.addstr(y, x, ch, attr)

    # __________________________________________________________________
    # Methods that work with files

    def write(self, filename):
        """ Save this puzzle to `filename`. """

        info_obj = {
                'groups': self.groups,
                'size'  : self.size
        }

        wrapper_obj = {
                'format_name'   : 'kkpuzzle',
                'format_url'    : '<pending>',
                'format_version': '0.1',
                'info'          : info_obj
        }

        with open(filename, 'w') as f:
            json.dump(wrapper_obj, f)

    def read(self, filename):
        with open(filename) as f:
            data = json.load(f)
        assert 'format_name' in data and data['format_name'] == 'kkpuzzle'
        info = data['info']
        self.size = info['size']
        self.groups = [
                [tuple(pt) for pt in group]
                for group in info['groups']
        ]


# ______________________________________________________________________
# Functions

# A debug print function.
def dbgpr(*args):
    pass
