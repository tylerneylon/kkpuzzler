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
import time

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
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        puzzle.read(filename)

    x0, y0 = refresh_screen(puzzle)

    movements = {'h': (-1, 0), 'j': (0, 1), 'k': (0, -1), 'l': (1, 0)}
    leader_state = 0

    is_in_leader_state = False

    while True:
        puzzle.draw(stdscr, x0, y0)
        stdscr.refresh()
        key = stdscr.getkey()
        leader_state = max(leader_state - 1, 0)

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

            if leader_state:
                # Auto-choose a filename.
                date_str = time.strftime('%Y_%m_%d')
                n = puzzle.size
                filename = f'puzzle_{n}x{n}_{date_str}.kk'
            else:
                line = drawing.get_line(stdscr, ':w ')
                if line != '':
                    filename = f'{line}.kk'
                elif filename is None:
                    show_status('Not saved: No filename given or known.')
                    continue

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

            # The user may potentially want to edit multiple clues here.
            while True:
                final_char = puzzle.edit_clue(stdscr)
                if final_char is None:
                    break
                dir_ = 'reading' if final_char == 'n' else movements[final_char]
                pt = puzzle.get_next_clueless_point(dir_)
                if pt is None:
                    if final_char in 'hjkl':
                        for i in range(2):
                            puzzle.cursor[i] += movements[final_char][i]
                            puzzle.cursor[i] = puzzle.cursor[i] % puzzle.size
                    break
                else:
                    puzzle.cursor = list(pt)

        elif key == 'f':              #### f    = Figure it out! (full soln)

            start_time = time.time()
            solns = solver.solve_puzzle(puzzle)
            time_to_solve = time.time() - start_time
            if len(solns) > 0:
                # XXX
                dbg.print('Adding the solution:', solns[0])
                puzzle.add_solution(solns[0])
                show_status(f'Found a solution in {time_to_solve:.2f}s.')

        elif key == '\\':             #### \    = Leader.

            leader_state = 2

if __name__ == '__main__':
    curses.wrapper(main)
