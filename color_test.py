# From:
# https://stackoverflow.com/a/22166613/3561

import curses

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    for i in range(0, 255):
        stdscr.addstr(f'{i} ', curses.color_pair(i + 1))

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, -1, i)
    for i in range(0, 255):
        stdscr.addstr(f'{i} ', curses.color_pair(i + 1))

    stdscr.getch()

curses.wrapper(main)
