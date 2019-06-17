from sources import *
from email_util import EmailServer

import time


class PollingServer:
    """Represents a polling server that continuously checks the internet for new used car listings."""

    def __init__(self, searches: list, callback_email: str = "aaronjencks@gmail.com", interval: int = 60):
        self.callback_email = callback_email
        email_server = EmailServer()
        self.sources = [CarGurus(self.callback_email, searches, email_server=email_server, auto_start=False),
                        CarsDotCom(self.callback_email, searches, email_server=email_server, auto_start=False)]
        self.interval = interval
        self.is_running = False

    def idle(self):
        """Continuously polls for new vehicle listings"""
        start = time.time()
        while self.is_running:
            if time.time() - start > self.interval * 60:
                start = time.time()
                for s in self.sources:
                    s.find_new_listings()
            else:
                print_notification("Waiting for the next update in {} seconds".format(
                    round(self.interval * 60 - (time.time() - start), 2)), begin='\r', end='')
                time.sleep(1)
                # time.sleep(self.interval * 60 - (time.time() - start))

    def start(self):
        self.is_running = True
        for s in self.sources:
            s.start()
        self.idle()

    def stop(self):
        self.is_running = False
