from display_util.string_display_util import print_notification
from email_util import EmailServer

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

    # region JSON

    def to_json(self) -> dict:
        return {'type': 'Car', 'make': self.make, 'model': self.model, 'year': self.year,
                'mileage': self.mileage, 'price': self.price, 'url': self.url}

    @staticmethod
    def from_json(data: dict):
        return Car(data['make'], data['model'], data['year'], data['mileage'], data['price'], data['url'])

    # endregion


class Model:
    def __init__(self, name: str, mileage: int = 100000, years: tuple = (-1, -1)):
        self.name = name
        self.mileage = mileage
        self.year_start = years[0]
        self.year_end = years[1]

    # region JSON

    def to_json(self) -> dict:
        return {'type': 'Model', 'name': self.name, 'mileage': self.mileage,
                'year_start': self.year_start, 'year_end': self.year_end}

    @staticmethod
    def from_json(data: dict):
        return Model(data['name'], data['mileage'], (data['year_start'], data['year_end']))

    # endregion


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

    # region JSON

    def to_json(self) -> dict:
        result = {'type': 'Search', 'make': self.make, 'models': [],
                  'year_start': self.year_start, 'year_end': self.year_end, 'mileage': self.mileage,
                  'zip': self.zip, 'distance': self.distance,
                  'price_start': self.price_start, 'price_end': self.price_end}

        for m in self.models:
            if isinstance(m, Model):
                result['models'].append(m.to_json())
            else:
                # Should be a string
                result['models'].append({'type': 'string', 'value': m})

        return result

    @staticmethod
    def from_json(data: dict):
        result = Search(data['make'], [], data['mileage'], (data['year_start'], data['year_end']),
                        data['zip'], data['distance'], data['price_start'], data['price_end'])

        for m in data['models']:
            if m['type'] == 'string':
                result.models.append(m['value'])
            elif m['type'] == 'Model':
                result.models.append(Model.from_json(m))

        return result

    # endregion


class Source:
    def __init__(self, searches: list, browser=None, auto_start: bool = True):
        self.searches = searches
        self.browser = webdriver.Firefox() if browser is None else browser

        self.timeout_delay = 10

        self.cars_db = []
        self.new_cars = []

        if auto_start:
            self.find_new_listings()

    def __del__(self):
        if self.browser is not None:
            self.browser.close()

    def on_new_listing(self, car: Car):
        print_notification("Found car: {}".format(car))
        pass

    def find_new_listings(self):
        pass

    # region JSON

    def to_json(self) -> dict:
        return {'type': 'Source', 'searches': [x.to_json() for x in self.searches],
                'cars': [x.to_json() for x in self.cars_db], 'timeout_delay': self.timeout_delay}

    @staticmethod
    def from_json(data: dict):
        searches = [Search.from_json(x) for x in data['searches']]

        # TODO Add support for other browsers
        result = Source(searches, auto_start=False)
        result.timeout_delay = data['timeout_delay']
        result.cars_db = [Car.from_json(x) for x in data['cars']]

        return result

    # endregion


class EmailingSource(Source):
    """Same as a normal source, except that 'on_new_listing' emails the target email address."""

    def __init__(self, target_email: str, searches: list, browser=None, smtp_server: EmailServer = None, auto_start: bool = True):
        super().__init__(searches, browser, False)

        if smtp_server is None:
            smtp_server = EmailServer()

        self.email_server = smtp_server
        self.email_callback = target_email

        if auto_start:
            self.start()

    def __del__(self):
        super().__del__()
        if self.email_server.is_running:
            self.email_server.stop()

    def start(self):
        self.email_server.start()
        self.find_new_listings()

    def create_email(self, car: Car) -> str:
        """Creates an email string composed of the car's information"""
        return """
        <html>
          <body>
            <p><b>[AUTOMATED EMAIL, DO NOT REPLY]</b><br>
            <br>
            A car of the requirements that you specified has just been listed<br>
            <a href={}>{}</a><br>
            <br>
            Best,<br>
            <br>
            Jarvis</p>
          </body>
        </html>
        """.format(car.url, str(car))

    def on_new_listing(self, car: Car):
        super().on_new_listing(car)

        email = self.create_email(car)

        self.email_server.send_mail(self.email_callback, str(car), email)

    # region JSON

    def to_json(self) -> dict:
        result = super().to_json()

        result['server'] = self.email_server.to_json()
        result['email callback'] = self.email_callback

        return result

    @staticmethod
    def from_json(data: dict):
        searches = [Search.from_json(x) for x in data['searches']]

        # TODO Add support for other browsers
        result = EmailingSource(searches, auto_start=False)
        result.timeout_delay = data['timeout_delay']
        result.cars_db = [Car.from_json(x) for x in data['cars']]

        result.email_server = EmailServer.from_json(data['server'])
        result.email_callback = data['email callback']

        return result

    # endregion



