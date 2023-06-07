import re

from bs4 import BeautifulSoup, Tag
from selenium.common import TimeoutException
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from models.text import Text
from models.browser import get_driver, scroll_down


class Ozon:
    domain_url: str = "https://www.ozon.ru"
    search_input: (str, str) = (By.TAG_NAME, "input")
    content_selen: (str, str) = (By.CLASS_NAME, "widget-search-result-container")
    content_bs: (str, str) = ("div", "widget-search-result-container")
    card: (str, str) = (By.CLASS_NAME, "product-card__main")
    tags: (str, str) = (By.CLASS_NAME, "search-tags__header")
    product_img: (str, str) = (By.CLASS_NAME, 'product-card__img')


def all_prices_parsing(text: str) -> tuple:
    # Текущая и старая цена товара
    no_spaces = re.sub(r'[\s.,-]', '', text)
    split_symbol = re.search(r'\D+', no_spaces)[0]

    # Решаем следующую ситуацию: ['124728', '191890', ''] -> ['124728', '191890']
    return tuple(int(price) for price in no_spaces.split(split_symbol) if price)


def comments_reviews_parsing(spans: list[Tag]):
    reviews = comments = 0
    for span in spans:
        val = span.text
        clear_val = re.sub(r'\s|[^a-zA-Z0-9_.,]', '', val)
        if clear_val and not re.findall(r'[^0-9.,]', clear_val):
            if re.search(r'[.,]', clear_val):
                reviews = float(clear_val)
            else:
                comments = int(clear_val)
    return reviews, comments


def parse_soup_html_v1(input_name, card_elems):
    """ Парсинг карточек товаров, когда они располагаются горизонтальными плашками """
    text_matcher = Text()
    res = []
    for card in card_elems:
        card_divs = card.find_all('div', recursive=False)

        comments_info = card_divs[1].find('div').find_all('div', recursive=False)
        if comments_info:
            comments_info = comments_info[-1].find('div').find_all('span', recursive=False)
        else:
            comments_info = []
        reviews, comments = comments_reviews_parsing(comments_info)

        prices_tag = card_divs[2].find_next('span').text
        if len(re.findall(r'[^0-9\s]', prices_tag)) > len(re.findall(r'[0-9]', prices_tag)):
            prices_tag = card_divs[2].find_next('div').text
        prices = all_prices_parsing(prices_tag)
        current_price = min(prices)
        goods_name = card_divs[1].find_next('a').text

        res.append({
            "url": f"{Ozon.domain_url}{card.find('a').get('href')}",
            "img": card.find('img').get('src'),
            "current_price": current_price,
            "reverse_price": (1 / current_price) if current_price != 0 else 0,
            "old_price": max(prices),
            "brand_name": None,
            "goods_name": goods_name,
            "reviews": reviews,
            "comments": comments,
            "market": "ozon",
            "text_accuracy": text_matcher.text_accuracy(input_name, goods_name)
        })
    return res


def parse_soup_html_v2(input_name, card_elems):
    """ Парсинг карточек товаров, когда они располагаются сеткой """
    text_matcher = Text()
    res = []
    for card in card_elems:
        card_divs = card.find_all('div', recursive=False)

        comments_info = card_divs[0].find_all('div', recursive=False)[-2].find_all('span', recursive=False)
        reviews, comments = comments_reviews_parsing(comments_info)

        prices_tag = card_divs[0].find_all('div', recursive=False)[0].text
        prices = all_prices_parsing(prices_tag)
        current_price = min(prices)

        goods_name = card_divs[0].find_next('a').text

        res.append({
            "url": card.find('a').get('href'),
            "img": card.find('img').get('src'),
            "current_price": current_price,
            "reverse_price": (1 / current_price) if current_price != 0 else 0,
            "old_price": max(prices),
            "brand_name": None,
            "goods_name": goods_name,
            "reviews": reviews,
            "comments": comments,
            "market": "ozon",
            "text_accuracy": text_matcher.text_accuracy(input_name, goods_name)
        })
    return res


def main(input_name: str, driver: Chrome = None):
    if not driver:
        driver = get_driver()

    driver.get(Ozon.domain_url)

    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(Ozon.search_input))
    elem = driver.find_element(*Ozon.search_input)  # ищем первый input

    elem.clear()
    elem.send_keys(input_name + Keys.ENTER)

    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located(Ozon.content_selen))
    except TimeoutException:
        driver.refresh()

    scroll_down(driver, 1.5)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    card_elems = html_soup.find(*Ozon.content_bs).find_next("div").find_all("div", recursive=False)

    if len(card_elems[0].find_all('div', recursive=False)) == 4:
        res = parse_soup_html_v1(input_name, card_elems)
    else:
        res = parse_soup_html_v2(input_name, card_elems)

    driver.close()
    return res


# from pprint import pprint
# pprint(main("чашка"))
