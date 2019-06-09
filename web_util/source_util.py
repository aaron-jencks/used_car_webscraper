from display_util.string_display_util import print_notification

from selenium import webdriver


class Car:
    def __init__(self, make: str, model: str, year: int, mileage: int, price: int, url: str):
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.price = price
        self.url = url

    def __str__(self):
        return "{} {} {}, ${}, {} miles".format(self.year, self.make, self.model, self.price, self.mileage)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.make == other.make and self.model == other.model and self.year == other.year and \
                   self.mileage == other.mileage and self.price == other.price
        else:
            return False


class Model:
    def __init__(self, name: str, mileage: int = 100000, years: tuple = (-1, -1)):
        self.name = name
        self.mileage = mileage
        self.year_start = years[0]
        self.year_end = years[1]


class Search:
    def __init__(self, make: str, models: list, mileage: int = 100000, years: tuple = (-1, -1),
                 zip: int = 52405, distance: int = 100, price_start: int = 0, price_end: int = -1):
        self.make = make
        self.models = models
        self.year_start = years[0]
        self.year_end = years[1]
        self.mileage = mileage
        self.zip = zip
        self.distance = distance
        self.price_start = price_start
        self.price_end = price_end


class Source:
    def __init__(self, searches: list, browser=None, auto_start: bool = True):
        self.searches = searches
        self.browser = webdriver.Firefox() if browser is None else browser

        self.cars_db = []
        self.new_cars = []

        if auto_start:
            self.find_new_listings()

    def __remove_dollar_and_comma(self, data: str) -> int:
        """Removes the $ and , from the labels on the display for the price sliders."""
        return int(data.replace('$', '').replace(',', ''))

    def on_new_listing(self, car: Car):
        # TODO: Have email me
        print_notification("Found car: {}".format(car))
        pass

    def find_new_listings(self):
        pass
