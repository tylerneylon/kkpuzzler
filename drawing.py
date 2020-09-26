""" drawing.py

    The main function here is add_box_char(), which provides a user-friendly
    interface to render line-drawings, often referred to as "box-drawing," in a
    terminal.

    Here are the box-drawing characters used, along with their direction sets;
    the direction set is the key input to add_box_char():

     ─ 0x2500 {'right', 'left'}

     ┌ 0x250c {'right', 'down'}

     ┐ 0x2510 {'left', 'down'}

     ┬ 0x252c {'right', 'left', 'down'}

     └ 0x2514 {'right', 'up'}

     ┘ 0x2518 {'left', 'up'}

     ┴ 0x2534 {'right', 'left', 'up'}

     │ 0x2502 {'down', 'up'}

     ├ 0x251c {'right', 'down', 'up'}

     ┤ 0x2524 {'left', 'down', 'up'}

     ┼ 0x253c {'right', 'left', 'down', 'up'}

    Useful links:

    * https://en.wikipedia.org/wiki/Box-drawing_character
    * https://docs.python.org/3/howto/curses.html
    * https://docs.python.org/3/library/curses.html
"""


# ______________________________________________________________________
# Imports

import curses
import curses.textpad


# ______________________________________________________________________
# Public functions

def add_char(stdscr, y, x, dirs, name_char=False):
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
    if name_char:
        stdscr.addstr(y, x + 2, hex(chr_code))

# Modify Textbox behavior to work better with backspaces.
class Textbox(curses.textpad.Textbox):

    def edit(self, validate=None):
        self.did_escape = False
        return super().edit(validate)

    # This is the main modification. We handle character 127 as delete, and
    # character 27 as escape, which causes a None return value.
    def do_command(self, ch):
        with open('commands.txt', 'a') as f:
            f.write(str(ch))
            f.write('\n')
        if ch == 127:
            ch = curses.KEY_BACKSPACE
        if ch == 27:
            self.did_escape = True
            return False
        return super().do_command(ch)

    def gather(self):
        if self.did_escape:
            return None
        return super().gather()

def get_line(stdscr, prompt=''):
    """ Collect a line of input from the user. This is a long-running
        synchronous operation.
    """
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h - 1, 0, prompt)
    stdscr.refresh()
    subwin = stdscr.subwin(h - 1, len(prompt))
    textbox = Textbox(subwin)
    prev_state = curses.curs_set(1)
    # Give the user control for a bit. What could go wrong?
    value = textbox.edit()
    curses.curs_set(prev_state)
    stdscr.addstr(h - 1, 0, ' ' * (w - 1))
    stdscr.refresh()
    return None if value is None else value.rstrip()

# TODO: Either drop this or make it more general.
def draw_grid(stdscr):

    xmin, xmax = 64, 128
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
