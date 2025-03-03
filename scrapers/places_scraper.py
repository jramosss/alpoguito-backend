from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options as DriverOptions

from scrapers.Scraper import Scraper
from utils.constants import ALPOGO_URL
from models.Place import Place
import requests
import toolz


class PlacesScraper(Scraper):
    driver: webdriver.Chrome | None

    def __init__(
        self,
        *,
        pages_to_scrape=3,
        time_to_wait=0.5,
        driver_options: DriverOptions = None,
    ):
        options: DriverOptions = driver_options or DriverOptions()
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=options,
        )
        self.pages_to_scrape = pages_to_scrape
        self.time_to_wait = time_to_wait
        super().__init__()

    def load_pages(self):
        for i in range(self.pages_to_scrape):
            self.driver.find_element(by=By.ID, value="cargar-eventos").click()
            sleep(self.time_to_wait)

    @staticmethod
    def __get_place_id_from_href(href: str):
        return int(href.split("/")[-1])

    @staticmethod
    def __get_place_image(place_url: str):
        page = requests.get(place_url)
        soup = BeautifulSoup(page.text, "html.parser")
        img_element = soup.find("img", class_="background-banda")
        return img_element["src"] if img_element else ""

    def create_place(self, place_element: WebElement):
        try:
            href = place_element.get_attribute("href")
            splitted_name = place_element.text.split(",")
            name = splitted_name[0]
            location = splitted_name[1] if len(splitted_name) > 1 else ""
            print("place", name, href)
            return Place(
                name=name,
                url=href,
                id=self.__get_place_id_from_href(href),
                image_url=self.__get_place_image(href),
                location=location.strip(),
            )
        except Exception as e:
            print(f"Error creating place {place_element}")
            print(e)
            return None

    def create_places(self, places_elements: list[WebElement]):
        with ThreadPoolExecutor(max_workers=6) as executor:
            return list(executor.map(self.create_place, places_elements))

    def find_places(self):
        places_elements = self.driver.find_elements(
            by=By.CLASS_NAME, value="lugar-link"
        )
        places_elements = [place for place in places_elements if place.text]
        return list(toolz.unique(places_elements, key=lambda x: x.text))

    def get_page(self):
        self.driver.get(f"{ALPOGO_URL}")

    def scrape(self):
        self.get_page()
        self.driver.implicitly_wait(self.time_to_wait)
        self.load_pages()
        places_elements = self.find_places()
        return self.create_places(places_elements)

    def teardown(self):
        # self.driver.quit()
        pass
