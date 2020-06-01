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

                if len(dirs) > 0:
                    box_drawing.add_char(stdscr, y, x, dirs)
                    continue

                ch = ' '

                # Check to see if this is a cursor character.
                if self.cursor:
                    grid_x = (x - x0) // self.x_stride
                    grid_y = (y - y0) // self.y_stride

                    if tuple(self.cursor) == (grid_x, grid_y):
                        ch = '*'

                stdscr.addstr(y, x, ch)


# ______________________________________________________________________
# Functions


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

if __name__ == '__main__':
    curses.wrapper(main)

    print(f'key = {key}')
