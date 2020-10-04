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
import sys

import dbg
import drawing
import solver
from puzzle import Puzzle


# ______________________________________________________________________
# Globals

stdscr = None


# ______________________________________________________________________
# Functions

def show_status(status):
    global stdscr
    drawing.show_status(stdscr, status)

def refresh_screen(puzzle):
    """ Erase the screen and recalculate the upper-left corner of a puzzle.
        This is useful when either the screen or the puzzle is resized, or
        on initialization.
    """

    global stdscr
    stdscr.erase()

    puzzle_size_x = puzzle.size * puzzle.x_stride
    puzzle_size_y = puzzle.size * puzzle.y_stride
    h, w = stdscr.getmaxyx()
    x0 = (w - puzzle_size_x) // 2
    y0 = (h - puzzle_size_y) // 2

    return x0, y0


# ______________________________________________________________________
# Main

def main(stdscr_):

    # I use a global for `stdscr` to simplify sharing it with other functions
    # (like show_status()) within this file.
    global stdscr
    stdscr = stdscr_

    curses.curs_set(False)  # Hide the text cursor.
    stdscr.clear()

    puzzle = Puzzle(6)
    puzzle.cursor = [0, 0]

    # Check to see if we should load a puzzle.
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        puzzle.read(filename)

    x0, y0 = refresh_screen(puzzle)

    movements = {'h': (-1, 0), 'j': (0, 1), 'k': (0, -1), 'l': (1, 0)}

    while True:
        puzzle.draw(stdscr, x0, y0)
        stdscr.refresh()
        key = stdscr.getkey()

        if key == 'q' or key == 'Q':  #### qQ   = Quit

            break

        elif key in 'hjkl':           #### hjkl = cursor movement

            for i in range(2):
                puzzle.cursor[i] += movements[key][i]
                puzzle.cursor[i] = puzzle.cursor[i] % puzzle.size

        elif key in 'HJKL':           #### HJKL = group editing

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

        elif key == 'w':              #### w    = Write (save) to a file

            line = drawing.get_line(stdscr, ':w ')
            filename = f'{line}.kk'
            puzzle.write(filename)
            show_status(f'Puzzle written to {filename}')

        elif key == 's':              #### s    = set the puzzle Size

            line = drawing.get_line(stdscr, ':s ')
            try:
                new_size = int(line)
            except:
                show_status(f'Unable to parse as an integer: "{line}"')
                continue
            puzzle.reset_size(new_size)
            x0, y0 = refresh_screen(puzzle)

        elif key == 'c':              #### c    = set the Clue

            final_char = puzzle.edit_clue(stdscr)
            if final_char:
                for i in range(2):
                    puzzle.cursor[i] += movements[final_char][i]
                    puzzle.cursor[i] = puzzle.cursor[i] % puzzle.size

        elif key == 'f':              #### f    = Figure it out! (full soln)

            solns = solver.solve_puzzle(puzzle)
            if len(solns) > 0:
                # XXX
                dbg.print('Adding the solution:', solns[0])
                puzzle.add_solution(solns[0])

if __name__ == '__main__':
    curses.wrapper(main)
