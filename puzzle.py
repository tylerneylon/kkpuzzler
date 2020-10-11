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
CLUE            = 4


# ______________________________________________________________________
# Main class

class Puzzle(object):

    # __________________________________________________________________
    # Constructor

    def __init__(self, size=4):
        # Each group has the form [<clue_str>, <pt1>, <pt2>, <pt3>, ... ].
        # Some points may be in no groups (for new/partial puzzles).
        self.groups = []
        self.size = size
        self.solution = None

        self.x_stride = 11
        self.y_stride = 5

        # These are convenient to have around.
        self.add_char = '+'
        self.sub_char = '–'
        self.mul_char = '×'
        self.div_char = '÷'
        self.op_chars = ''.join([
            self.add_char,
            self.sub_char,
            self.mul_char,
            self.div_char
        ])

        # I am considering allowing self.cursor == None, which would indicate
        # we're in a display-only mode. This might be interesting for simply
        # viewing a puzzle (like `cat FILE`), or printing a puzzle.
        self.cursor = [0, 0]

        # The format here is (index, foreground, background).
        curses.init_pair(GROUP_HIGHLIGHT, 246, 234)
        curses.init_pair(BACKGROUND, 7, 16)
        curses.init_pair(CLUE, 241, 16)

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

        # We drop any clue from the old group being split.
        new_a_group = ['']
        new_b_group = ['']
        for pt in orig_group[1:]:  # [1:] to skip the clue.
            # TODO I've occasionally seen this next line throw an IndexError.
            #      I don't know exactly how to reproduce the error. The last
            #      time I saw it, I was splitting up a large group into two
            #      pieces, and I had to do it in mini-splits because the larger
            #      group was strongly connected. Maybe run this via ipython -i
            #      and try to %debug from there. Another route would be to try
            #      to trigger ipdb on a caught exception here, but I'm not 100%
            #      sure if the curses mode would mess up how we interact with
            #      ipdb (I've seen ipython -i work from curses, so I'm more
            #      confident about that approach).
            path = self.find_all_paths(pt, b, orig_group)[0]
            if a in path:
                new_a_group.append(pt)
            else:
                new_b_group.append(pt)

        self.groups.remove(orig_group)
        if len(new_a_group) > 2: self.groups.append(new_a_group)
        if len(new_b_group) > 2: self.groups.append(new_b_group)

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
            a_group[0][1].extend(b_group[0][1][1:])  # [1:] to skip b's clue.
            del self.groups[b_group[0][0]]
        elif a_group or b_group:
            dbgpr('Clause 2')
            grp = a_group[0][1] if a_group else b_group[0][1]
            if a not in grp: grp.append(a)
            if b not in grp: grp.append(b)
        else:
            dbgpr('Clause 3')
            self.groups.append(['', a, b])

        # XXX
        dbgpr('At end of join, self.groups =', self.groups)

    def set_clue_at_cursor(self, clue):
        group = self.get_group_at_cursor()
        group[0] = clue

    def add_solution(self, soln):
        self.solution = soln

    # __________________________________________________________________
    # Utility methods

    def get_next_clueless_point(self, dir_):
        """ This searches for the next group, starting from, and excluding,
            self.cursor, and looking in the direction `dir_`. `dir_` can either
            be a tuple such as (1, 0), or the string 'reading', indicating that
            we're looking for the next group in reading order with wrap-around.

            If no clueless group exists in the direction given, None is
            returned. Otherwise, the appropriate point within that group is
            returned.
        """

        if type(dir_) is tuple:
            new_pt = [self.cursor[i] + dir_[i] for i in range(2)]
            while 0 <= new_pt[0] < self.size and 0 <= new_pt[1] < self.size:
                group = self.get_group_at_point(new_pt)
                if group[0] == '':
                    return tuple(new_pt)
                new_pt = [new_pt[i] + dir_[i] for i in range(2)]
            return None
        else:
            assert dir_ == 'reading'
            new_pt = self.cursor[:]
            while True:
                new_pt[0] += 1
                if new_pt[0] == self.size:
                    new_pt = [0, (new_pt[1] + 1) % self.size]
                if new_pt == self.cursor:
                    return None  # We've searched the whole puzzle.
                group = self.get_group_at_point(new_pt)
                if group[0] == '':
                    return tuple(new_pt)

    def get_group_at_point(self, pt):
        """ If `pt` is in a group, this returns that group (as a list).
            Otherwise, this creates a new group with the contents
            ['', <pt>], appends this group to self.groups, and returns
            the new group. """
        groups = [g for g in self.groups if tuple(pt) in g]
        assert len(groups) < 2

        if len(groups) > 0:
            return groups[0]

        # We need to create a new group.
        group = ['', tuple(pt)]
        self.groups.append(group)
        return group

    def get_group_at_cursor(self):
        """ If the cursor is in a group, this returns that group (as a list).
            Otherwise, this creates a new group with the contents
            ['', <cursor_point>], appends this group to self.groups, and returns
            the new group. """
        return self.get_group_at_point(self.cursor)

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

    def get_clue_point(self, group):
        """ Return the point in group that ought to include the clue.
            This is the first square in the group in Enslish reading order; ie,
            we read lines left-to-right, starting at the top. """
        return sorted(
                group[1:],  # [1:] to skip the clue string.
                key=lambda pt: self.size * pt[1] + pt[0]
        )[0]

    def get_top_y_value(self, group):
        """ Return the top (numerically smallest) y value found in the group.
        """
        clue_pt = self.get_clue_point(group)
        return clue_pt[1]

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
            self.cursor = list(self.get_clue_point(group))
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
            cursor. This lets the user finish editing by hitting one of the hjkl
            keys, in which case that key (as a one-char str) is returned;
            otherwise None is returned.
        """
        assert self.cursor

        # A `subline` is (y, x1, x2).
        subline = self.jump_to_clue_subline(stdscr)
        clue, final_char = drawing.edit_subline(
                stdscr,
                subline,
                extra_end_chars='hjkln'
        )
        if clue is None:
            return
        # TODO: Pull the official op characters out into constants that are
        #       shared across files. Currently this one and solver.py.
        op_mapping = {
                '+': self.add_char,
                '-': self.sub_char,
                'x': self.mul_char,
                '*': self.mul_char,
                '/': self.div_char
        }
        if clue[-1] in op_mapping:
            clue = clue[:-1] + op_mapping[clue[-1]]
        # TODO: Check if clue strings are valid. If not, we can highlight
        #       them in red so users can correct them.
        self.set_clue_at_cursor(clue)
        return final_char

    def draw(self, stdscr, x0, y0):

        # TODO Call this only once.
        stdscr.bkgd(' ', curses.color_pair(BACKGROUND))

        current_group = ['', tuple(self.cursor)]
        for group in self.groups:
            if tuple(self.cursor) in group:
                current_group = group
        current_group_top_y = self.get_top_y_value(current_group)

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

                # If we get here, we're drawing in-square (not-border) chars.

                ch = ' '
                attr = curses.color_pair(0)

                # Check to see if this is a cursor character.
                if self.cursor and x1 == x2 and y1 == y2:
                    if tuple(self.cursor) == (x1, y1):
                        if (y - y0) % self.y_stride != 1:
                            ch = '.'
                        attr = curses.color_pair(GROUP_HIGHLIGHT)
                    if (x1, y1) in current_group:
                        attr = curses.color_pair(GROUP_HIGHLIGHT)
                        # if y1 == current_group_top_y:
                        if (y - y0) % self.y_stride == 1:
                            attr = curses.color_pair(0)

                stdscr.addstr(y, x, ch, attr)

        # Render the clues.
        for group in self.groups:
            if group[0] == '':
                continue
            clue_pt = self.get_clue_point(group)
            x = x0 + clue_pt[0] * self.x_stride + 1
            y = y0 + clue_pt[1] * self.y_stride + 1
            clue_str = '%%-%ds' % (self.x_stride - 1) % group[0]
            stdscr.addstr(y, x, clue_str, curses.color_pair(CLUE))

        # Render the solution if we have one.
        if self.solution is None:
            return
        for i, num in enumerate(self.solution):
            x = x0 + (i % self.size)  * self.x_stride + 5
            y = y0 + (i // self.size) * self.y_stride + 3
            stdscr.addstr(y, x, str(num), curses.color_pair(0))

    # __________________________________________________________________
    # Methods that work with files

    def write(self, filename):
        """ Save this puzzle to `filename`. """

        info_obj = {
                'groups'  : self.groups,
                'size'    : self.size,
                'solution': self.solution
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
        self.solution = info.get('solution', None)
        self.groups = [
                # Ensure each group list has a string followed by tuples.
                [group[0]] + [tuple(pt) for pt in group[1:]]
                for group in info['groups']
        ]


# ______________________________________________________________________
# Functions

# A debug print function.
def dbgpr(*args):
    pass
