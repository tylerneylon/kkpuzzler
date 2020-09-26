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

import drawing
from puzzle import Puzzle


# ______________________________________________________________________
# Main

def main(stdscr):

    # XXX
    global key

    curses.curs_set(False)  # Hide the text cursor.
    stdscr.clear()

    h, w = stdscr.getmaxyx()
    # stdscr.addstr(2, 2, f'max (x, y) = ({x}, {y})')  # XXX

    puzzle = Puzzle(6)
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
        elif key == 'w':
            line = drawing.get_line(stdscr, ':w ')
            # TODO: Actually save to a file. Probably put this in a fn.

if __name__ == '__main__':
    curses.wrapper(main)

    print(f'key = {key}')
