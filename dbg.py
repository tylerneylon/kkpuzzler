""" dbg.py

    This is a script to support debug printing from a curses-based application.

    To use this module (as a developer):

        * Call dbg.print() instead of print() for your debug prints.
        * In a separate window, run `tail -f dbg.out` to see debug output live.
"""


# ______________________________________________________________________
# Imports

from datetime import datetime


# ______________________________________________________________________
# Globals

dbgout = open('dbg.out', 'a')


# ______________________________________________________________________
# Functions

def print(*args, **kwargs):
    end = kwargs.get('end', '\n')
    dbgout.write(' '.join(args) + end)
    dbgout.flush()


# ______________________________________________________________________
# Initialization

# Print out a header each time this module starts up. Users are likely to leave
# `tail -f dbg.out` running in a separate terminal window, and this headers
# helps to visually distinguish one run from the next.
print('\n')
print('_' * 70)
print('New run starting at', datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
print()
