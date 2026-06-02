#!/usr/bin/python

"""
Utility functions for TCD1304 CCD Controller.

Provides helper functions for string parsing, data generation, and I/O operations.
"""

import sys
import inspect
import select
import numpy as np

try:
    import regex
    HAS_REGEX = True
except ImportError:
    import re as regex
    HAS_REGEX = False


def lineno():
    """Get the current line number in the calling code."""
    return inspect.currentframe().f_back.f_lineno


def errorprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def input_ready():
    """Check if keyboard input is available on stdin."""
    return sys.stdin in select.select([sys.stdin], [], [], 0)[0]


def key_in_list(ls, key, mapf=str):
    """
    Find a key in a list and return the next value, optionally mapped.
    
    Args:
        ls: List to search
        key: Key to find
        mapf: Function to apply to the next value (default: str)
    
    Returns:
        Mapped value at ls[idx+1] or None if not found
    """
    try:
        idx = ls.index(key)
        return mapf(ls[idx + 1])
    except (ValueError, IndexError):
        return None


def generate_x_vector(npoints, coefficients=None):
    """
    Generate an x-axis vector for wavelength or pixel coordinates.
    
    Args:
        npoints: Number of points
        coefficients: Optional polynomial coefficients for coordinate mapping
    
    Returns:
        numpy array of x values, optionally transformed by polynomial
    """
    x = np.linspace(0, npoints, npoints)

    if coefficients is None:
        return x
    else:
        return np.polynomial.polynomial.polyval(x, coefficients)


def split_nested(string):
    """
    Find nested parentheses using recursive regex.
    
    Args:
        string: String to search
    
    Returns:
        regex Match object or None
    """
    result = regex.search(
        r'''
        (?<rec> #capturing group rec
        \( #open parenthesis
        (?: #non-capturing group
        [^()]++ #anything but parenthesis one or more times without backtracking
        | #or
        (?&rec) #recursive substitute of group rec
        )*
        \) #close parenthesis
        )
        ''',
        string,
        regex.VERBOSE
    )
    return result


def split_bracketed(string, delimiter=' ', strip_brackets=False):
    """
    Split a string by delimiter, respecting bracket nesting.
    
    Example:
        list(split_bracketed('abc,(def,ghi),jkl', delimiter=','))
        returns ['abc', '(def,ghi)', 'jkl']
    
    Args:
        string: String to split
        delimiter: Character to split on (default: space)
        strip_brackets: If True, remove outer brackets from split parts
    
    Yields:
        String parts split by delimiter outside brackets
        
    Raises:
        AssertionError: If bracket nesting is unbalanced
    
    (Based on stackoverflow question 21662474)
    """
    openers = '[{(<'
    closers = ']})>'
    opener_to_closer = dict(zip(openers, closers))
    opening_bracket = {}
    current_string = ''
    depth = 0
    
    for char in string:
        if char in openers:
            depth += 1
            opening_bracket[depth] = char
            if strip_brackets and depth == 1:
                continue
        elif char in closers:
            assert depth > 0, (
                f"Unmatched closing bracket in string: {string}"
            )
            assert char == opener_to_closer[opening_bracket[depth]], (
                f"Mismatched brackets: closing {char} doesn't match "
                f"opening {opening_bracket[depth]} in {string}"
            )
            depth -= 1
            if strip_brackets and depth == 0:
                continue
        
        if depth == 0 and char == delimiter:
            yield current_string
            current_string = ''
        else:
            current_string += char
    
    assert depth == 0, f"Unclosed brackets in string: {string}"
    yield current_string
