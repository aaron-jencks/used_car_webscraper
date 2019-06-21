from polling_server import *
from email_util import EmailServer
from display_util.string_display_util import *
from display_util.menu import *

import threading
from collections import deque


class Main(threading.Thread):
    def __init__(self):
        super().__init__()
        self.state_queue = deque()
        self.default_state = self.main_menu
        self.is_stopping = False

        self.searches = []
        self.server = PollingServer(self.searches)

        # Global Search settings
        self.year_start = -1
        self.year_stop = -1
        self.mileage = -1
        self.price_start = -1
        self.price_stop = -1
        self.zipcode = -1
        self.radius = -1

    def run(self):
        """Starts a state machine that manages the gui"""
        while not self.is_stopping:
            if len(self.state_queue) == 0:
                self.default_state()
            else:
                state = self.state_queue.popleft()
                state()

    def stop(self):
        self.is_stopping = True

    def start_server(self):
        self.server = PollingServer(self.searches)
        self.server.start()

    def edit_searches(self):
        pass

    def edit_search_settings(self):
        """This is the search settings menu for the program, asks the user if they want to edit the current searches,
        edit global search constraints, change the search distance or zipcode, or go back."""
        choice = 0

        while choice != 5:
            choice = console_dash_menu({1: 'Edit Search List', 2: 'Edit Global Constraints',
                                        3: 'Edit Zipcode', 4: 'Edit Search Distance', 5: 'Back'},
                                       title="Used Car Webscraper: Search Settings")

            def numeric_validator(v: str) -> bool:
                try:
                    int(v)
                    return True
                except:
                    pass
                finally:
                    return False

            if choice == 1:
                self.state_queue.append(self.edit_searches)

            elif choice == 2:
                globals_choice = 1

                while globals_choice != 4:

                    globals_choice = console_dash_menu({1: 'Edit Year Range', 2: 'Edit Price Range',
                                                        3: 'Edit Maximum Mileage', 4: 'Back'},
                                                       title="Global Search Settings Menu")

                    if globals_choice == 1:
                        def year_validator(v: str) -> bool:
                            try:
                                if len(v.split()) == 2:
                                    start = int(v.split()[0])  # Try to convert them into ints, might throw an exception
                                    stop = int(v.split()[1])
                                    return True
                                else:
                                    return False
                            except:
                                pass
                            finally:
                                """One of the values was not a number"""
                                return False

                        print_info("The current year range is: ({} to {})".format(self.year_start, self.year_stop))
                        y_range = get_constrained_input("Please enter a year range "
                                                        "in the form of 'start stop' including the space "
                                                        "(use -1 if you don't want to supply that argument): ",
                                                        year_validator)

                        y_start, y_stop = y_range.split()

                        self.year_start = int(y_start)
                        self.year_stop = int(y_stop)
                        continue

                    elif globals_choice == 2:
                        def price_validator(v: str) -> bool:
                            try:
                                if len(v.split()) == 2:
                                    start = int(v.split()[0])  # Try to convert them into ints, might throw an exception
                                    stop = int(v.split()[1])
                                    return True
                                else:
                                    return False
                            except:
                                pass
                            finally:
                                """One of the values was not a number"""
                                return False

                        print_info("The current price range is: ({} to {})".format(
                            insert_dollar_sign_and_commas(self.price_start),
                            insert_dollar_sign_and_commas(self.price_stop)))
                        p_range = get_constrained_input("Please enter a price range "
                                                        "in the form of 'start stop' including the space, "
                                                        "don't use commas or dollar signs "
                                                        "(use -1 if you don't want to supply that argument): ",
                                                        price_validator)

                        p_start, p_stop = p_range.split()

                        self.price_start = int(p_start)
                        self.price_stop = int(p_stop)
                        continue

                    elif globals_choice == 3:

                        print_info("The current maximum mileage is: {}".format(self.mileage))
                        miles = get_constrained_input("Please enter a maximum mileage to use, use -1 for default: ",
                                                      numeric_validator)

                        self.mileage = int(miles)

                    elif globals_choice == 4:
                        break

            elif choice == 3:
                print_info("The current zipcode is: {}".format(self.zipcode))
                t_zip = get_constrained_input("Please enter a 5-digit zipcode: ",
                                              lambda x: len(x) == 5 and numeric_validator(x))
                self.zipcode = int(t_zip)

            elif choice == 4:
                print_info("The current search radius is: {}".format(self.radius))
                t_rad = get_constrained_input("Please enter a new radius: ",
                                              numeric_validator)
                self.radius = int(t_rad)

            elif choice == 5:
                break

    def edit_server_settings(self):
        """This is the server settings menu for the program, asks the user if they want to edit the refresh rate,
        email settings, or go back"""
        choice = 0

        while choice != 3:
            choice = console_dash_menu({1: 'Edit Server Refresh Rate', 2: 'Edit Email Settings', 3: 'Back'},
                                       title="Used Car Webscraper: Server Settings")

            # TODO
        pass

    def main_menu(self):
        """This is the main menu for the program, asks the user if they want to start, edit settings, or quit."""
        choice = console_dash_menu({1: 'Start Server', 2: 'Edit Search Settings', 3: 'Edit Server Settings', 4: 'Exit'},
                                   title="Used Car Webscraper: Main Menu")
        if choice == 1:
            if len(self.searches) == 0:
                print_error("The list of searches is empty! Please add at least one search!")
                self.state_queue.append(self.main_menu)
            elif self.zipcode < 0:
                print_error("The zipcode cannot be less than 0, please enter one in the search settings menu!")
                self.state_queue.append(self.main_menu)
            else:
                self.state_queue.append(self.start_server)

        elif choice == 2:
            self.state_queue.append(self.edit_search_settings)

        elif choice == 3:
            self.state_queue.append(self.edit_server_settings)

        elif choice == 4:
            self.state_queue.append(self.stop)


if __name__ == "__main__":
    m = Main()
    m.start()
    m.join()
