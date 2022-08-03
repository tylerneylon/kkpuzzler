# -*- coding: utf-8 -*-
"""
    sevendate.py

    A small module to convert a datetime into a 7date string, or to convert a
    7date string into a datetime.

    The purpose of this file is to make it easier for you to integrate 7date
    support into a program that already uses Gregorian dates.

    Sample usage:

        $ python3 sevendate.py
        160.2022

        $ python3 sevendate.py 0.2040
        2040-01-01 00:00:00

        $ python sevendate.py 10.2040  # One week later.
        2040-01-08 00:00:00

    See the 7date specification here:
    http://tylerneylon.com/a/7date_spec/
"""


# ___________________________________________________________________________
# Imports

import sys
from datetime import datetime
from datetime import timedelta


# ___________________________________________________________________________
# Functions

# This expects n and b to be integers with n >= 0 and b > 1.
# This returns the number n written in base b, as a string.
def tobase(n, b):
    assert n >= 0 and b > 1
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    digits = digits if digits else [0]
    return ''.join(map(str, reversed(digits)))

# This converts string s, which is expected to have digits 0 through (b-1),
# into a Python number, which is returned.
# This assumes 1 < b <= 10, and that s represents a nonnegative integer.
def frombase(s, b):
    assert 1 < b <= 10
    n = 0
    for char in s:
        n *= b
        d = ord(char) - ord('0')
        if not 0 <= d < b:
            raise ValueError(f'Invalid digit in base-{b} number "{s}"')
        n += d
    return n

# This expects a valid 7date string (either standard or digital format); it
# returns a datetime object for the beginning of the given day.
# If there is a parsing error, this throws a ValueError.
def to_datetime(sevendate_str):
    sevendate_str = sevendate_str.strip()  # Ignore surrounding whitespace.
    dot = sevendate_str.find('.')
    if dot == -1:
        # Assume it's in digital format, which is YYYY-DDDD.
        year_str = sevendate_str[0:4]
        day_str  = sevendate_str[5:]
    else:
        # Assume it's in standard format, which is D+.YYYY.
        day_str  = sevendate_str[:dot]
        year_str = sevendate_str[dot + 1:]
    day_num  = frombase(day_str, 7)
    year_num = int(year_str)
    time = datetime(year_num, 1, 1) + timedelta(days=day_num)
    return time

# This expects either None or a datetime string. If you pass in None (or no
# arguments), it provides the 7date string.
def to_string(time=None, do_use_digital_format=False):
    if time is None:
        time = datetime.now()
    year = str(time.year)
    day  = tobase(time.timetuple().tm_yday - 1, 7)
    if do_use_digital_format:
        # The format specifier "0>4s" means "right-align (>) the string (s) in
        # `day`, and pad with '0' chars to achieve minimum length 4."
        # https://peps.python.org/pep-3101/#standard-format-specifiers
        return f'{year}-{day:0>4s}'
    else:
        return f'{day}.{year}'


# ___________________________________________________________________________
# Main

if __name__ == '__main__':

    # Check to see if perhaps a 7date string was provided to us.
    if len(sys.argv) > 1 and sys.argv[1] != '-d':

        sevendate_str = sys.argv[1]
        print(str(to_datetime(sevendate_str)))

    else:  # Otherwise, provide the 7date string for today.

        do_use_digital_format = ('-d' in sys.argv)
        print(to_string(do_use_digital_format=do_use_digital_format))
