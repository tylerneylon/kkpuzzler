""" edit_puzzle.py

    This is a script to edit a KenKen puzzle.

    Use the h/j/k/l keys to move the cursor left/down/up/right.

    Hold shift to use H/J/K/L to merge the current square with the
    square left-of/below/above/right-of the cursor.
"""


# ______________________________________________________________________
# Imports

import curses

import box_drawing


# ______________________________________________________________________
# Classes

# TODO: Eventually move this class into its own file.

class Puzzle(object):

    def __init__(self, size):
        self.groups = []
        self.size = size

        self.x_stride = 10
        self.y_stride = 5

        self.cursor = None

    def draw(self, stdscr, x0, y0):

        xmax = x0 + self.size * self.x_stride
        ymax = y0 + self.size * self.y_stride

        for x in range(x0, xmax + 1):
            for y in range(y0, ymax + 1):

                dirs = set()
                if (x - x0) % self.x_stride == 0:
                    dirs |= {'up', 'down'}
                if (y - y0) % self.y_stride == 0:
                    dirs |= {'left', 'right'}

                if x == x0:
                    dirs -= {'left'}
                if y == y0:
                    dirs -= {'up'}
                if x == xmax:
                    dirs -= {'right'}
                if y == ymax:
                    dirs -= {'down'}

                # Check to see if this is a cursor character.
                if len(dirs) == 0 and self.cursor:
                    grid_x = (x - x0) // self.x_stride
                    grid_y = (y - y0) // self.y_stride

                    if self.cursor == (grid_x, grid_y):
                        stdscr.addstr(y, x, '*')

                box_drawing.add_char(stdscr, y, x, dirs)



# ______________________________________________________________________
# Functions


# ______________________________________________________________________
# Main

def main(stdscr):

    # XXX
    global key

    curses.curs_set(False)  # Hide the text cursor.
    stdscr.clear()

    y, x = stdscr.getmaxyx()
    stdscr.addstr(2, 2, f'max (x, y) = ({x}, {y})')

    puzzle = Puzzle(7)
    puzzle.cursor = (0, 0)

    while True:
        puzzle.draw(stdscr, 10, 10)
        stdscr.refresh()
        key = stdscr.getkey()

        if key == 'q' or key == 'Q':
            break

if __name__ == '__main__':
    curses.wrapper(main)

    print(f'key = {key}')
