import shutil
from colorama import Fore
import os

import sys
import traceback

from .list_display_util import get_list_entry_str, ListTypes


def clear():
    """Clears the terminal screen as per
    https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console"""
    if os.name in ('nt','dos'):
        os.system("cls")
    elif os.name in ('linux','osx','posix'):
        os.system("clear")
    else:
        print("\n"*120)


def replace_tabs(string: str, tab_width: int = 4) -> str:
    """Takes an input string and a desired tab width and replaces each \\t in the string with ' '*tab_width."""

    return string.replace('\t', ' '*tab_width)


def centered_text(text: str, length: int = -1) -> str:
    """Returns a string that contains enough spaces to center the text in the context of the length given

    Defaults to centering the text in the width of the entire console

    text is stripped of leading and trailing whitespace before starting

    If length - len(text) is odd, then the extra space is appended to the end of the string

    If len(text) >= length, then text is returned

    If length is wider than the terminal width, then it is squeezed to fit

    Note: This does add spaces to the end of the string, not just the beginning, this allows for an accurate size in
    conjunction with other functions in this library"""

    t = text.strip()

    # If length is longer than the console width, then squeeze it to fit
    num_col = shutil.get_terminal_size((80, 20)).columns
    if length > num_col:
        length = num_col

    if len(t) >= length:
        return t

    space_tot = length - len(t)
    space_num = space_tot // 2

    space = " "*space_num

    if space_tot % 2 == 0:
        return space + t + space
    else:
        # Places the extra space at the end of the string
        return space + t + space + " "


def dashed_line(num: int, dash: str = '#') -> str:
    """Returns a string composed of num dashes"""

    temp = ""
    for i in range(num):
        temp += dash

    return temp


def print_dashes(num: int, dash: str = '#'):
    """Prints out a single line of dashes with num chars
    If the num is larger than the console width, then a single console width is printed out instead"""

    # Gets the terminal width
    num_col = shutil.get_terminal_size((80, 20)).columns

    print(dashed_line(num if num <= num_col else num_col, dash))


def hanging_indent(string: str, tab_width: int = 4) -> str:
    """Creates a hanging indent """

    # Gets the terminal width
    num_col = shutil.get_terminal_size((80, 20)).columns

    if len(string) <= num_col:
        # Returns a clone of the string, not the original
        return string[:]

    # Creates a tab string
    tab = " "*tab_width

    result = string[:num_col]
    remaining = string[num_col:]
    while True:
        if len(remaining) > num_col - tab_width:
            result += tab + remaining[:num_col - tab_width]
            remaining = remaining[num_col - tab_width:]
        else:
            result += tab + remaining
            break

    return result


def print_list(arr: list, format: str = "{}: {}", l_type: ListTypes = ListTypes.NUMERIC_ORDERED, **kwargs):
    """Prints a list to the screen in a neat fashion.

    format is a string used to determine layout of the element, default is '{}: {}' where the first is the index,
        and the second is the element."""

    for i, e in enumerate(arr):
        print(get_list_entry_str(e, i, format, l_type), **kwargs)


def print_info(string: str, begin: str = '', **kwargs):
    """Prints an info prompt to the console
    info prompts have '[INFO]' as a prefix and are printed in Yellow."""
    print(begin + Fore.YELLOW + "[INFO] " + string + Fore.RESET, **kwargs)


def print_warning(string: str, begin: str = '', **kwargs):
    """Prints an warning prompt to the console
    warning prompts have '[WARNING]' as a prefix and are printed in Red."""
    print(begin + Fore.RED + "[WARNING] " + string + Fore.RESET, **kwargs)


def print_error(string: str, begin: str = '', **kwargs):
    """Prints an error prompt to the console
    error prompts have '[ERROR]' as a prefix and are printed in Red."""
    print(begin + Fore.RED + "[ERROR] " + string + Fore.RESET, **kwargs)


def print_exception(begin: str = '', **kwargs):
    """Prints the current exception out to the console using the '[ERROR]' as a prefix and is printed in red.
    First line contains '[ERROR] Exception was thrown: <exception string>'
    Second line and on contains the full typical python traceback."""
    et, ev, tb = sys.exc_info()
    exc = begin + "Exception was thrown: {}\n".format(ev)
    for l in traceback.format_exception(et, ev, tb):
        exc += l
    print_warning(exc)


def print_notification(string: str, begin: str = '', **kwargs):
    """Prints an notification prompt to the console
    notification prompts have '[NOTIFICATION]' as a prefix and are printed in Green."""
    print(begin + Fore.GREEN + "[NOTIFICATION] " + string + Fore.RESET, **kwargs)
