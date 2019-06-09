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
                        self.__remove_dollar_and_comma(mileage) if mileage != "N/A" else -1,            # mileage
                        self.__remove_dollar_and_comma(price) if price != "No Price Listed" else -1,    # price
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

                lower_bound = self.__remove_dollar_and_comma(
                    self.browser.find_element_by_id("priceSliderLowerBoundaryLabel").text)

                upper_bound = self.__remove_dollar_and_comma(
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

                lower_bound = self.__remove_dollar_and_comma(
                    self.browser.find_element_by_id("mileageSliderLowerBoundaryLabel").text.split()[0])

                upper_bound = self.__remove_dollar_and_comma(
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

    def find_new_listings(self):
        # TODO
        for i, s in self.searches:
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
        pass


if __name__ == "__main__":
    guru = CarGurus([Search("Toyota", ["Camry", "Avalon"], price_end=8000)])
