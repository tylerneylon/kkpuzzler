#!/usr/bin/env python3
""" edit_puzzle.py

    This is a script to edit a KenKen puzzle.

    Use the h/j/k/l keys to move the cursor left/down/up/right.

    Hold shift to use H/J/K/L to merge the current square with the
    square left-of/below/above/right-of the cursor.
"""


# ______________________________________________________________________
# Imports

# Standard library imports.
import curses
import inspect
import math
import os
import shlex
import sys
import time

# Local imports.
import dbg
import drawing
import event
import partition
import sevendate
import solver
from pdf_maker import make_pdf
from puzzle    import Puzzle


# ______________________________________________________________________
# Globals

stdscr = None


# ______________________________________________________________________
# Functions

status_tick = None
status_str  = ''

def fade_out_status(num_ticks):
    global stdscr, status_tick, status_str
    ticks_passed = num_ticks - status_tick
    fade_time_in_ticks = 20
    if ticks_passed > fade_time_in_ticks:
        return
    color = 254 - ticks_passed
    # dbg.print(f'Drawing status in color {color}.')
    drawing.show_status(stdscr, status_str, color=color)
    stdscr.refresh()

def show_status(status):
    global stdscr, status_tick, status_str
    drawing.show_status(stdscr, status)
    status_str  = status
    status_tick = event.num_ticks
    if fade_out_status not in event.callbacks:
        event.callbacks.append(fade_out_status)

def clear_status():
    global stdscr
    if fade_out_status in event.callbacks:
        event.callbacks.remove(fade_out_status)
    drawing.show_status(stdscr, '')

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

def draw_help_screen():
    """ Erase the screen and render the help screen, which explains which keys
        do what. You can toggle this screen by pressing '?'.
    """

    global stdscr

    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # helplines is a list of key explanations.
    helplines = inspect.cleandoc(r"""
        hjkl Move the cursor. Wrap-around possible.
        HJKL Join or split a group via this movement.
        gg   Jump to the top-left of the puzzle.
        p    Save a pdf file of this puzzle (no solution).
        \p   Save a pdf file that includes the solution.
        o    Save the puzzle to a pdf and open the pdf file.
        e    Run the experimental puzzle solver.
        f    Find the solution to the given puzzle.
        c    Start editing clues at the current group.
        s    Set the puzzle size.
        w    Type a filename, this puzzle is saved to that file.
        \w   Save to a file, choosing a default name if needed.
        q    Quit.
        ?    See this help screen :)
    """).split('\n')

    cell_width  = max(map(len, helplines))
    cell_height = 2
    num_rows = math.ceil(len(helplines) / 2)
    mid_pad  = 5

    x0 = (w - mid_pad - 2 * cell_width) // 2
    y0 = (h - cell_height * num_rows) // 2

    def show_cell(cell_x, cell_y, text):
        ''' Print `text` at 0-indexed position (cell_x, cell_y) in a centered
            table with num_rows rows and cell sizes cell_{width,height}.
        '''
        x = x0 + (cell_width + mid_pad) * cell_x
        y = y0 + cell_height * cell_y
        stdscr.addstr(y, x, text)

    def show_centered(y, text):
        x = (w - len(text)) // 2
        stdscr.addstr(y, x, text)

    # Draw header text.
    show_centered(y0 - 5, '--== Keyboard shortcuts ==--')
    show_centered(y0 - 4, '_' * 60)

    # Draw the help lines.
    cell_x, cell_y, i = 0, 0, 0
    while i < len(helplines):
        show_cell(cell_x, cell_y, helplines[i])
        i += 1
        cell_x += 1
        if cell_x == 2:
            cell_x = 0
            cell_y += 1

    show_status('Press any key to exit the help screen!')
    key = stdscr.getkey()
    stdscr.erase()
    show_status('')

def get_default_filename(puzzle):
    date_str = sevendate.to_string(do_use_digital_format=True)
    date_str = date_str.replace('-', '_')
    if False:
        # You can use this instead for Gregorian dates.
        date_str = time.strftime('%Y_%m_%d')
    n = puzzle.size
    return f'puzzle_{n}x{n}_{date_str}.kk'

def make_pdf_using_puzzle_filename(
        puzzle,
        puzzle_filename,
        does_include_solution=False):

    pdf_filename = puzzle_filename
    if pdf_filename is None:
        pdf_filename = get_default_filename(puzzle)
    suffix = '_w_soln' if does_include_solution else ''
    pdf_filename = pdf_filename.split('.', 1)[0] + suffix + '.pdf'
    make_pdf(puzzle, pdf_filename, does_include_solution)

    return pdf_filename

def update_availale_partitions(stdscr, puzzle):
    """ Evaluate which values can possibly fill the current group in the puzzle
        based on the clue and the shape of the group. Display these values for
        the user if we're in the correct mode; as of this writing, such modes
        are not yet implemented.

        In some cases, valid values cannot be found. For example, if there is no
        cursor, or if there is no clue.
    """
    group = puzzle.get_group_at_cursor()

    part_fn_map = {
            puzzle.add_char: partition.get_add_partitions,
            puzzle.sub_char: partition.get_sub_partitions,
            puzzle.mul_char: partition.get_mul_partitions,
            puzzle.div_char: partition.get_div_partitions
    }

    clue = group[0]

    if clue == '':
        return

    op_char = clue[-1]
    if op_char in puzzle.op_chars:
        num_sq = len(group) - 1
        group_w = len({pt[0] for pt in group[1:]})
        group_h = len({pt[1] for pt in group[1:]})
        max_repeat = min(group_w, group_h)
        parts = part_fn_map[op_char](
                puzzle.size,
                int(clue[:-1]),
                num_sq,
                max_repeat
        )
    else:
        parts = [[int(clue)]]

    dbg.print(parts)


# ______________________________________________________________________
# Main

def main(stdscr_):

    # I use a global for `stdscr` to simplify sharing it with other functions
    # (like show_status()) within this file.
    global stdscr
    stdscr = event.Window(stdscr_)

    dbg.print(stdscr.__class__)

    curses.halfdelay(1)     # Add a timeout to getkey().
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

    leader, prev_leader = '', ''

    show_status('Press ? to see the help screen.')

    while True:

        puzzle.draw(stdscr, x0, y0)
        stdscr.refresh()
        leader, prev_leader = '', leader

        # TODO Be able to respond meaningfully to ctrl-C.
        key = stdscr.getkey()

        if key == 'q' or key == 'Q':  #### qQ   = Quit

            break

        elif key in 'hjkl':           #### hjkl = cursor movement

            for i in range(2):
                puzzle.cursor[i] += movements[key][i]
                puzzle.cursor[i] = puzzle.cursor[i] % puzzle.size

            update_availale_partitions(stdscr, puzzle)

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

            if prev_leader != '\\':
                clear_status()
                line = drawing.get_line(stdscr, ':w ')
                if line is None:
                    show_status(f'Write canceled')
                    continue
                if line:
                    filename = line + ('' if line.endswith('.kk') else '.kk')

            if filename is None:
                filename = get_default_filename(puzzle)

            puzzle.write(filename)
            show_status(f'Puzzle written to {filename}')

        elif key == 's':              #### s    = set the puzzle Size

            clear_status()
            line = drawing.get_line(stdscr, ':s ')
            if line is None:
                show_status(f'Size change canceled')
                continue
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

            # TODO Error gracefully if we don't have all the clues.

            start_time = time.time()
            solns = solver.solve_puzzle(puzzle)
            time_to_solve = time.time() - start_time
            if len(solns) > 0:
                # XXX
                dbg.print('Adding the solution:', solns[0])
                puzzle.add_solution(solns[0])
                show_status(f'Found a solution in {time_to_solve:.2f}s.')

        elif key == 'e':              #### e    = run Experimental solver.

            solver.print_human_friendly_soln(puzzle)

        elif key == 'p':

            if prev_leader != '\\':   #### p    = make a Pdf of this puzzle.

                pdf_filename = make_pdf_using_puzzle_filename(puzzle, filename)
                show_status(f'pdf written to {pdf_filename}')

            else:                     #### \p   = make a pdf incl the soln.

                # Ensure a solution is known.
                if puzzle.solution is None:
                    show_status('Finding a solution ...')
                    puzzle.add_solution(solver.solve_puzzle(puzzle)[0])
                pdf_filename = make_pdf_using_puzzle_filename(
                        puzzle,
                        filename,
                        does_include_solution = True
                )
                show_status(f'pdf written to {pdf_filename}')

        elif key == 'o':              #### o    = Open a pdf of this puzzle.

            pdf_filename = make_pdf_using_puzzle_filename(puzzle, filename)
            show_status(f'pdf written to {pdf_filename}')
            os.system(f'open {shlex.quote(pdf_filename)}')

        elif key == '\\':             #### \    = Leader.

            leader = '\\'

        elif key == 'g':              #### g    = Leader.

            if prev_leader == 'g':  # gg = jump to (0, 0).
                puzzle.cursor = [0, 0]
            else:
                leader = 'g'

        elif key == '?':

            draw_help_screen()


if __name__ == '__main__':
    curses.wrapper(main)
