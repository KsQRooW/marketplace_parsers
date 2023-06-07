"""
Для отладки:
# with open('html_test.html', 'w', encoding='utf-8') as file:
#     file.write(BeautifulSoup(driver.page_source, 'lxml').prettify())
"""

import re

from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from models.text import Text
from models.browser import get_driver, scroll_down


class WildBerries:
    domain_url: str = "https://www.wildberries.ru"
    search_input: (str, str) = (By.ID, 'searchInput')
    content: (str, str) = (By.CLASS_NAME, "main-page")
    card_selen: (str, str) = (By.CLASS_NAME, "catalog-page__main")
    card_bs: (str, str) = ("div", "product-card__wrapper")
    product_img: (str, str) = ("div", 'product-card__img-wrap')
    product_prices: (str, str) = ("p", "product-card__price")
    product_brand_name: (str, str) = ("span", 'product-card__brand')
    product_goods_name: (str, str) = ("span", 'product-card__name')
    comments_info: (str, str) = ("span", "product-card__rating")


def all_prices_parsing(text: str) -> tuple:
    # Текущая и старая цена товара
    no_spaces = re.sub(r'[\s.,-]', '', text)
    split_symbol = re.search(r'\D', no_spaces)[0]

    # Решаем следующую ситуацию: ['124728', '191890', ''] -> ['124728', '191890']
    return tuple(int(price) for price in no_spaces.split(split_symbol) if price)


def parse_soup_html(input_name, card_elems):
    text_matcher = Text()
    res = []
    for card in card_elems:
        img = card.find(*WildBerries.product_img).find('img').get('src')
        prices = all_prices_parsing(card.find(*WildBerries.product_prices).text)
        comments_info = card.find(*WildBerries.comments_info)
        goods_name = card.find(*WildBerries.product_goods_name).text
        current_price = min(prices)
        res.append({
            "url": card.find_next('a').get('href'),
            "img": img if img.startswith("https") else f"https:{img}",
            "current_price": current_price,
            "reverse_price": (1 / current_price) if current_price != 0 else 0,
            "old_price": max(prices),
            "brand_name": card.find(*WildBerries.product_brand_name).text,
            "goods_name": goods_name,
            "reviews": float(comments_info.get('class')[-1][-1]) if comments_info else 0,
            "comments": int(re.sub(r'\D', '', comments_info.find_next('span').text)) if comments_info else 0,
            "market": "wildberries",
            "text_accuracy": text_matcher.text_accuracy(input_name, goods_name)
        })
    return res


def main(input_name: str, driver: Chrome = None):
    if not driver:
        driver = get_driver()

    driver.get(WildBerries.domain_url)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located(WildBerries.content))
    elem = driver.find_element(*WildBerries.search_input)

    elem.clear()
    elem.send_keys(input_name + Keys.ENTER)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(WildBerries.card_selen))

    scroll_down(driver, delay=0.5)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    card_elems = html_soup.find_all(*WildBerries.card_bs)

    res = parse_soup_html(input_name, card_elems)

    driver.close()
    return res
