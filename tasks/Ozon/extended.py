import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from functions.timer import timer
from models.browser import get_driver, scroll_down
from tasks.translator.main import translate
from tasks.summarizator.main import summarize


@timer
def parse_extend(url: str, driver=None):
    if not driver:
        driver = get_driver()

    driver.get(url)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "snow-ali-kit_Typography__base__1shggo")))
    html_soup = BeautifulSoup(driver.page_source, features="lxml")

    img_urls = html_soup.find("img", "lj c9-a")
    final_price = int(re.sub(r'[\D\s.,-]', '', html_soup.find("div", "snow-price_SnowPrice__mainS__jlh6el").text))

    names_info = html_soup.find("h1", "snow-ali-kit_Typography__base__1shggo")
    brand_name = names_info.find('span').text
    product_name = names_info.find('h1').text


    params = {}
    all_div = html_soup.find_all("div", "SnowProductCharacteristics_SnowProductCharacteristicsItem__item__1w7g4")
    for div in all_div:
        params[div.find_next('span').text] = div.find_next('span').text

    scroll_down(driver)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    all_text = '. '.join(p.text for p in html_soup.find_all("li", "SnowReviewsList_SnowReviewsList__listItem__iqtrf"))

    translated_text = translate(driver, all_text, source="ru", target="en")
    summarized_text = summarize(translated_text)
    ru_summarized_text = translate(driver, summarized_text, source="en", target="ru")

    driver.close()
    return {
        "comments": ru_summarized_text,
        "price": final_price,
        "imgs": img_urls,
        "brand_name": brand_name,
        "product_name": product_name,
        "params": params
    }
