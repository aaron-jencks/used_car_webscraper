from display_util.string_display_util import print_notification
from web_util.source_util import Source, Search, Model, Car

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from tqdm import tqdm


class CarGurus(Source):
    def __init__(self, searches: list, browser=None, auto_start: bool = True):
        super().__init__(searches, browser, auto_start=False)

        self.value_source_url = "https://www.cargurus.com/Cars/forsale"

        if auto_start:
            self.find_new_listings()

    def __find_price_percentage(self, price: int, lower: int, upper: int, pixel_width: float) -> float:
        """Computes the percent of the slider that the node should be at and returns it"""
        diff = upper - lower
        adj_p = price - lower
        return adj_p / diff * pixel_width

    def __get_url(self, listing: int) -> str:
        """Finds the url for a corresponding listing and returns it"""
        current = self.browser.current_url
        result = ""
        result += current + "#listing=" + str(listing)

        return result

    def __find_car_list(self):
        """Runs through a series of search result pages and scrapes car objects off of them,
        appending them to a list of cars, if they don't already exist."""

        end_page = self.browser.find_element_by_class_name("toPage").text

        for i in range(int(end_page)):
            # Iterates through all of the pages
            for car in self.browser.find_elements_by_class_name("ft-car"):
                # Iterates through all of the cars on the page
                title = car.find_element_by_class_name("cg-dealFinder-result-model").text.split()

                stats = car.find_element_by_class_name("cg-dealFinder-result-stats").find_elements_by_tag_name("p")

                mileage = stats[3].text.split(':')[1].split()[0]
                price = stats[0].find_element_by_class_name(
                    "cg-dealFinder-priceAndMoPayment").find_element_by_tag_name("span").text

                c = Car(title[1], title[2], int(title[0]),                                              # make, model, year
                        self.remove_dollar_and_comma(mileage) if mileage != "N/A" else -1,            # mileage
                        self.remove_dollar_and_comma(price) if price != "No Price Listed" else -1,    # price
                        self.__get_url(int(car.get_attribute("onclick").split()[1][:-1])))              # url

                if c not in self.cars_db:
                    self.cars_db.append(c)
                    self.on_new_listing(c)

            if i < int(end_page) - 1:
                self.browser.find_element_by_class_name("nextPageElement").click()
        pass

    def find_new_listings(self):
        """Parses the global make list and downloads their models, then appends those options to the model_values"""
        print_notification("Filtering local makes")
        first = True

        for i, s in tqdm(enumerate(self.searches)):
            for model in s.models:

                self.browser.get(self.value_source_url)

                # region Fills out search field

                # region Make field

                make_dropdown = Select(self.browser.find_element_by_class_name("maker-select-dropdown"))

                make_dropdown.select_by_visible_text(s.make)

                # endregion

                model_dropdown = Select(self.browser.find_element_by_class_name("model-select-dropdown"))

                # region Enters region information

                if first:
                    zip_entry = self.browser.find_element_by_id("newSearchHeaderForm_UsedCar_zip")
                    zip_entry.send_keys(str(s.zip))

                    distance_dropdown = Select(self.browser.find_element_by_id("newSearchHeaderForm_UsedCar_distance"))
                    distance_dropdown.select_by_visible_text(str(s.distance) + " mi")

                    first = False

                # endregion

                is_model = isinstance(model, Model)
                model_dropdown.select_by_visible_text(model.name if is_model else model)

                year_dropdown = self.browser.find_elements_by_class_name("car-select-dropdown")

                yds = Select(year_dropdown[0])
                yde = Select(year_dropdown[1])

                if (is_model and model.year_start > 0) or s.year_start > 0:
                    yds.select_by_visible_text(str(model.year_start if is_model else s.year_start))

                if (is_model and model.year_end > 0) or s.year_end > 0:
                    yde.select_by_visible_text(str(model.year_end if is_model else s.year_end))

                form_submit = self.browser.find_element_by_class_name("newSearchSubmitButton")
                form_submit.click()

                # endregion

                # region Filters the results

                # region Price

                width = self.browser.find_element_by_class_name("ui-slider-range").size["width"]

                lower_bound = self.remove_dollar_and_comma(
                    self.browser.find_element_by_id("priceSliderLowerBoundaryLabel").text)

                upper_bound = self.remove_dollar_and_comma(
                    self.browser.find_element_by_id("priceSliderUpperBoundaryLabel").text)

                slider_low = self.browser.find_element_by_id("sliderHandle1Price")
                slider_up = self.browser.find_element_by_id("sliderHandle2Price")

                if s.price_start > 0:
                    action = ActionChains(self.browser)
                    action.drag_and_drop_by_offset(slider_low,
                                                   width - self.__find_price_percentage(
                                                       s.price_start, lower_bound, upper_bound, width), 0).perform()

                if s.price_end > 0:
                    action = ActionChains(self.browser)
                    action.drag_and_drop_by_offset(slider_up,
                                                   -1 * (width - self.__find_price_percentage(
                                                       s.price_end, lower_bound, upper_bound, width)), 0).perform()

                # endregion

                # region Mileage

                # width shouldn't have changed from the previous one

                lower_bound = self.remove_dollar_and_comma(
                    self.browser.find_element_by_id("mileageSliderLowerBoundaryLabel").text.split()[0])

                upper_bound = self.remove_dollar_and_comma(
                    self.browser.find_element_by_id("mileageSliderUpperBoundaryLabel").text.split()[0])

                # slider_low = self.browser.find_element_by_id("sliderHandle1mileage")
                slider_up = self.browser.find_element_by_id("sliderHandle2mileage")

                if 0 < s.mileage < upper_bound:
                    action = ActionChains(self.browser)
                    action.drag_and_drop_by_offset(slider_up,
                                                   -1 * (width - self.__find_price_percentage(
                                                       s.mileage, lower_bound, upper_bound, width)), 0).perform()

                # endregion

                # endregion

                self.__find_car_list()


class CarsDotCom(Source):
    def __init__(self, searches: list, browser=None, auto_start: bool = True):
        super().__init__(searches, browser, False)

        self.value_source_url = "https://www.cars.com"

        if auto_start:
            self.find_new_listings()

    def __binsearch(self, target: int, opts: list, data_conversion=lambda x: x) -> int:
        """Finds the closest value to the target in the given list of options."""
        left = 0
        right = len(opts)
        mid = -1

        while right > left:
            mid = left + (right - left) // 2

            if data_conversion(opts[mid]) == target:
                return mid
            elif data_conversion(opts[mid]) < target:
                left = mid + 1
                continue
            else:
                right = mid

        if data_conversion(opts[mid]) != target:
            return left - 1  # Always round down, don't show the user something out of their price range
        else:
            return mid

    def __insert_dollar_sign_and_commas(self, data: int) -> str:
        """Takes a string of numbers and inserts the '$' and ','"""
        return '${:,}'.format(data)

    def find_new_listings(self):
        # TODO
        for i, s in enumerate(self.searches):
            for model in s.models:
                self.browser.get(self.value_source_url)

                # region Make model price distance dropdowns

                # restricts to only used cars
                new_used_drop = Select(self.browser.find_element_by_css_selector("select[name='stockType']"))
                new_used_drop.select_by_visible_text("Used Cars")

                make_drop = Select(self.browser.find_element_by_css_selector("select[name='makeId']"))
                model_drop = Select(self.browser.find_element_by_css_selector("select[name='modelId']"))
                price_drop = Select(self.browser.find_element_by_css_selector("select[name='priceMax']"))
                distance_drop = Select(self.browser.find_element_by_css_selector("select[name='radius']"))

                # endregion

                is_model = isinstance(model, Model)

                make_drop.select_by_visible_text(s.make)
                model_drop.select_by_visible_text(model.name if is_model else model)

                # region Selects the closest price point in the price dropdown

                if s.price_end > 0:
                    closest = s.price_end
                    opts = price_drop.options

                    closest = opts[self.__binsearch(closest, sorted(opts,
                                                                    key=lambda x: self.remove_dollar_and_comma(x.text)
                                                                    if x.text != 'No Max Price' else -1),
                                                    lambda x: self.remove_dollar_and_comma(x.text)
                                                    if x.text != 'No Max Price' else -1)].text

                    price_drop.select_by_visible_text(closest)

                # endregion

                # region Selects the closest distance point in the distance dropdown

                closest = s.distance
                opts = distance_drop.options

                closest = opts[self.__binsearch(closest, sorted(opts,
                                                                key=lambda x: int(x.text.split()[0])
                                                                if x.text != 'All Miles from' else -1),
                                                lambda x: int(x.text.split()[0])
                                                if x.text != 'All Miles from' else -1)].text

                distance_drop.select_by_visible_text(closest)

                # endregion

                self.browser.find_element_by_css_selector("input[name='zip']").send_keys(str(s.zip))

                # Clicks the search button
                self.browser.find_element_by_css_selector("input[value='Search']").click()

                # region Filters the result

                # region Handles the lower price limit

                price_drop = Select(self.browser.find_element_by_css_selector("select[name='prMn']"))

                if s.price_start > 0:
                    closest = s.price_start
                    opts = price_drop.options

                    closest = opts[self.__binsearch(closest, sorted(opts,
                                                                    key=lambda x: self.remove_dollar_and_comma(
                                                                        x.text)),
                                                    lambda x: self.remove_dollar_and_comma(x.text))].text

                    price_drop.select_by_visible_text(closest)

                # endregion

                # region Handles the year ranges

                # TODO

                ydrops = self.browser.find_elements_by_css_selector("select[name='yrId']")

                ymin_drop = Select(ydrops[0])
                ymax_drop = Select(ydrops[1])

                # min
                if (is_model and model.year_start > 0) or s.year_start > 0:
                    closest = model.year_start if (is_model and model.year_start > 0) else s.year_start

                    opts = ymin_drop.options

                    closest = opts[self.__binsearch(closest, sorted(opts,
                                                                    key=lambda x: int(x.text)),
                                                    lambda x: int(x.text))]

                    ymin_drop.select_by_visible_text(str(closest))

                # max
                if (is_model and model.year_end > 0) or s.year_end > 0:
                    closest = model.year_end if (is_model and model.year_end > 0) else s.year_end

                    opts = ymax_drop.options

                    closest = opts[self.__binsearch(closest, sorted(opts,
                                                                    key=lambda x: int(x.text)),
                                                    lambda x: int(x.text))]

                    ymax_drop.select_by_visible_text(str(closest))

                # endregion

                # region Handles the mileage

                # TODO
                mileage_list = [y for y in [x.find_element_by_class_name("radio__label") for x in
                                self.browser.find_elements_by_class_name("radio")] if
                                y.get_attribute("for").startswith("mlgId-")]

                if (is_model and model.mileage > 0) or s.mileage > 0:
                    closest = model.mileage if is_model else s.mileage

                    closest = mileage_list[self.__binsearch(closest, sorted(mileage_list,
                                                                            key=lambda x: int(
                                                                                self.remove_dollar_and_comma(
                                                                                    x.text.split()[0]))),
                                                            lambda x: int(
                                                                self.remove_dollar_and_comma(
                                                                    x.text.split()[0])))]

                    # TODO get number after mlgId and use that to find the corresponding radio button.

                # endregion

                # endregion

        pass


if __name__ == "__main__":

    searches = [Search("Toyota", ["Camry", "Avalon"], price_end=8000)]

    # guru = CarGurus(searches)
    cars = CarsDotCom(searches)
