""" event.py

    A module to enable an asynchronous event loop in curses-based applications.

    NOTE: This class is designed to be useful when curses' getch() and getkey()
          methods have a timeout enabled, such as by calling curses.halfdelay().

    Sample usage:

        curses.halfdelay(1)

        def animation_step(num_ticks):
            animate_something(num_ticks)

        event.callbacks.append(animation_step)

        # Now animation_step will be called about once every 0.2 seconds, and
        # each time (aka each tick), it will receive the number of such 'ticks'
        # (intervals of about 0.2s) that have passed since the program started.
        # Note that this is _not_ multithreading, so there are plenty of ways
        # for your callback to _not_ be called in time. Specifically, this
        # relies on a loop in which a curses window has either getch() or
        # getkey() called often (at least once every tick).
"""


# ______________________________________________________________________
# Imports

import curses
import time


# ______________________________________________________________________
# Globals

# `callbacks` is meant to be publicly editable.
callbacks = []

# `num_ticks` is meant to be world-readable, but only internally written.
num_ticks = 0

# These are internal globals.
_start_time = time.time()


# ______________________________________________________________________
# Functions

def check_for_clock_tick():
    """ This function is called at least once every 0.1s.
        It ensures that all registered callbacks are called approximately
        every 0.2s.
        Since this function can be called _more often_ than every 0.1s, it
        regulates the rate further for the sake of the callbacks.

        To add a callback function, just append it to the `callbacks` global.
    """

    global _start_time, num_ticks, callbacks

    goal_num_ticks = (time.time() - _start_time) / 0.2
    while num_ticks < goal_num_ticks:
        num_ticks += 1
        for cb in callbacks:
            cb(num_ticks)



# ______________________________________________________________________
# Classes

class Window(object):

    def __init__(self, curses_window):
        self.curses_window = curses_window

    def __getattr__(self, key):
        return getattr(self.curses_window, key)

    def getkey(self):
        key = ''
        while key == '':
            try:
                key = self.curses_window.getkey()
            except curses.error as e:  # We may have a timeout.
                check_for_clock_tick()
        return key

    def getch(self):
        ch = -1
        while ch == -1:
            ch = self.curses_window.getch()
            check_for_clock_tick()
        return ch

    def subwin(self, *args):
        subwin = self.curses_window.subwin(*args)
        return Window(subwin)
