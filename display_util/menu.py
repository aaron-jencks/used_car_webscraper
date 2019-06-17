from .string_display_util import *
from .list_display_util import *
from colorama import Fore

from  copy import deepcopy


def get_constrained_input(prompt: str, constraint) -> str:
    """Prompts the user for input, continues to prompt the user for input until the lambda expression passed in for
        constraint returns True."""

    temp = input(Fore.GREEN + prompt + Fore.RESET)
    while not constraint(temp):
        print_warning("Invalid Response!")
        temp = input(Fore.GREEN + prompt + Fore.RESET)

    return temp


def yes_no_prompt(prompt: str = "") -> bool:
    """Prompts the user for a yes/no answer, automatically appends '(y/n) ' to your prompt.
    Returns True if the user answered yes, and False if they answered no."""

    choice = input(prompt + "(y/n) ")
    while choice != 'y' and choice != 'Y' and choice != 'n' and choice != 'N':
        print_warning("Invalid choice entered, please enter either 'y' or 'n'.")
        choice = input(prompt + "(y/n) ")

    return choice == 'y' or choice == 'Y'


def console_dash_menu(options: dict, list_format: str = "{}: {}", title: str = "", centered_title: bool = True,
                      dash: str = '#', tab_width: int = 4):
    """Creates a console style menu with the given options as choices to choose from
    Returns a key that was chosen from the options dict.
    Keys must be either a str or have a __str__() defined

    Arguments:

    options: a dict containing keys that are choices for users, and values that are descriptions for each key,
        the chosen key will be returned.

    list_format: uses similar syntax to str.format(), the default is \"{}: {}\" where the first {} is the key, and the
        second {} is the value.

    title: the title string displayed at the top of the menu.

    centered_title: True if the title string should be centered in the console.

    dash: character or string used as the duplicated dash sequence for the bars at the top and bottom of the menu.

    tab_width: width, in number of spaces, considered to be a single tab."""

    # Determines the longest string entry of the set of options
    entries = [list_format.format(k, options[k]) for k in options]
    max_length = max([len(x) for x in entries])
    if len(title) > max_length:
        max_length = len(title)

    # Creates the menu
    print_dashes(max_length, dash)
    print((centered_text(title, max_length) if centered_title else title) + "\n")
    print("Options: \n")
    for e in entries:
        print(hanging_indent(e, tab_width))

    print_dashes(max_length, dash)

    # Prompts the user for input and ensures validity
    valid = [str(k) for k in options.keys()]

    choice = get_constrained_input("Choice? ", lambda x: x in valid)

    # Finds the said choice and returns it
    index = valid.index(choice)
    return list(options.keys())[index]


def list_edit_menu(content: list, create_new_func, edit_func,
                   title: str = "", centered_title: bool = True, menu_entry_format: str = "{}: {}",
                   dash: str = '#', tab_width: int = 4,
                   l_type: ListTypes = ListTypes.NUMERIC_ORDERED,
                   inplace: bool = False, deep_copy: bool = False,
                   **kwargs) -> list:
    """Creates a menu for editting the list of items provided, displays the list according to the list type provided.

    Arguments:

    create_new_func: specifies a function used to create a new object for the list, returns the new object to insert.

    edit_func: specifies a function used to edit a current element, should return a copy to replace the original with.

    inplace: specifies if the operation should be performed on the existing memory object of content, or on a copy.

    deep_copy: specifies whether to perform a deepcopy of the list for the operation, or a shallow copy,
        only relevant if inplace is False.

    Any extra keyword arguments are passed along to the create and edit functions"""

    def init_lists(c: list) -> tuple:
        """Creates the selection dict for the list and the list of entry strings and finds the max length"""
        sd = {}
        es = []
        for i, e in enumerate(c):
            ef = get_list_entry_str(replace_tabs(str(e), tab_width), i, l_type=l_type)
            es.append(ef)
            sd[i] = ef

        ml = max([len(x) for x in es])

        return sd, es, ml

    selection_dict, entries, max_length = init_lists(content)

    def display_header():
        """Clears the terminal and displays the header information for the menu"""
        clear()
        if len(title) > 0:
            print(centered_text(title, max_length) if centered_title else title)
            print_dashes(max_length, dash)

        for e in entries:
            print(hanging_indent(e, tab_width))

        print_dashes(max_length, dash)

    display_header()
    choice = console_dash_menu({1: 'Create', 2: 'Edit', 3: 'Delete', 4: 'Exit'}, menu_entry_format,
                               "List Options", centered_title, dash, tab_width)

    def choose_selection():
        """Prompts the user to select an element out of the current content list"""
        clear()
        return console_dash_menu(selection_dict, menu_entry_format, "Which element would you like to choose?",
                                 centered_title, dash, tab_width)

    # Sets up the copy of the list if inplace if False
    temp = (deepcopy(content) if deep_copy else content[:]) if not inplace else []

    while choice != 4:
        if choice == 1:
            # Create new element
            el = create_new_func(**kwargs)
            if inplace:
                content.append(el)
            else:
                temp.append(el)

        elif choice == 2:
            # Edit an existing element
            index = choose_selection()
            el = edit_func(content[index] if inplace else temp[index])
            if inplace:
                content[index] = el
            else:
                temp[index] = el

        elif choice == 3:
            # Delete an existing element
            index = choose_selection()
            if inplace:
                content.pop(index)
            else:
                temp.pop(index)

        if inplace:
            selection_dict, entries, max_length = init_lists(content)
        else:
            selection_dict, entries, max_length = init_lists(temp)

        display_header()
        choice = console_dash_menu({1: 'Create', 2: 'Edit', 3: 'Delete', 4: 'Exit'}, menu_entry_format,
                                   "List Options", centered_title, dash, tab_width)

    if inplace:
        return content
    else:
        return temp
