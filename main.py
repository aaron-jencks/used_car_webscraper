from polling_server import *
from email_util import EmailServer
from display_util.string_display_util import *
from display_util.menu import *


if __name__ == "__main__":
    searches = [Search("Nissan", [Model("Versa")], price_end=8000),
                Search("Kia", [Model("Soul", years=(-1, 2012))], price_end=8000)]

    server = PollingServer(searches)
    server.start()
