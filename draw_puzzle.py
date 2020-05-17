""" drawpuzzle.py

    This is me learning how to use curses in python.
"""

import curses
import time

def start_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    return stdscr

def end_curses(stdscr):
    stdscr.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


# start_curses()
# end_curses()

def add_box_char(stdscr, y, x, dirs, name_char=False):
    """ Print a single box-drawing character at (x, y) based on the direction
        set given in `dirs`, which is expected to have elements from
        'up', 'down', 'left', 'right'. The `dirs` set cannot be a singleton.

        I have mixed feelings about this code. It works. Yet it is not at all
        beautiful. It seems no better than a lookup table. But I spent time
        figuring out how to do this in relatively few lines, so I'm leaving it
        here.
    """

    if len(dirs) == 0:
        return

    # The characters |, -, and + are special-cased here.
    if dirs == {'up', 'down'}:
        chr_code = 0x2502
    elif dirs == {'left', 'right'}:
        chr_code = 0x2500
    elif len(dirs) == 4:
        chr_code = 0x253c

    # All other cases are handled by the next block.
    else:
        chr_code = 0x24d4 + 0x1c * len(dirs)
        if 'left' in dirs:
            chr_code += 0x04
        if 'up' in dirs:
            chr_code += 0x08
        if len(dirs) > 2:
            if 'right' not in dirs:
                chr_code -= 0x10
            if 'left' not in dirs:
                chr_code -= 0x14

    stdscr.addstr(y, x, chr(chr_code))
    # TMP XXX
    if name_char:
        stdscr.addstr(y, x + 2, hex(chr_code))

def draw_grid(stdscr):

    xmin, xmax = 8, 64
    ymin, ymax = 8, 32

    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):

            dirs = set()
            if x % 4 == 0:
                dirs |= {'up', 'down'}
            if y % 2 == 0:
                dirs |= {'left', 'right'}

            if x == xmin:
                dirs -= {'left'}
            if y == ymin:
                dirs -= {'up'}
            if x == xmax:
                dirs -= {'right'}
            if y == ymax:
                dirs -= {'down'}

            add_box_char(stdscr, y, x, dirs)

def main(stdscr):

    global key

    curses.curs_set(False)

    stdscr.clear()
    stdscr.addstr(5, 5, 'why hello')

    stdscr.addstr(7, 7, chr(0x250c))  # UL /
    stdscr.addstr(7, 8, chr(0x2500))  # -
    stdscr.addstr(8, 7, chr(0x2502))  # |
    stdscr.addstr(7, 9, chr(0x253c))  # +
    stdscr.addstr(7,10, chr(0x2524))  # -|

    stdscr.addstr(13, 13, chr(0x2518))
    stdscr.addstr(12, 13, chr(0x2510))
    stdscr.addstr(12, 12, chr(0x250c))
    stdscr.addstr(13, 12, chr(0x2514))

    draw_grid(stdscr)

    # This is a little test for add_box_char().
    empty = set()
    x = 5
    y = 20
    for a in [empty, {'up'}]:
        for b in [empty, {'down'}]:
            for c in [empty, {'left'}]:
                for d in [empty, {'right'}]:
                    dirs = a.union(b).union(c).union(d)
                    if len(dirs) < 2:
                        continue
                    stdscr.addstr(y, x + 9, str(dirs))
                    add_box_char(stdscr, y, x, dirs, name_char=True)
                    y += 2



    stdscr.border()
    stdscr.refresh()
    key = stdscr.getkey()

curses.wrapper(main)
print(f'key is {key}')

def print_c(n, c):
    print(n, type(c), c, f'0x{c:x}')


print_c('VLINE', curses.ACS_VLINE)
print_c('HLINE', curses.ACS_HLINE)
print_c('LRCORNER', curses.ACS_LRCORNER)
print_c('URCORNER', curses.ACS_URCORNER)
print_c('LLCORNER', curses.ACS_LLCORNER)
print_c('ULCORNER', curses.ACS_ULCORNER)
