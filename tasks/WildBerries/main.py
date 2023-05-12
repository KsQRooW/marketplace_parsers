import random  # todo: выпилить

from pprint import pprint
import re
from time import sleep, time

from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager


class WildBerries:
    domain_url: str = "https://www.wildberries.ru"
    search_input: (str, str) = (By.ID, 'searchInput')
    content: (str, str) = (By.CLASS_NAME, "main-page")
    card_selen: (str, str) = (By.CLASS_NAME, "catalog-page__main")
    card_bs: (str, str) = ("div", "product-card__wrapper")
    tags: (str, str) = (By.CLASS_NAME, "search-tags__header")
    product_img: (str, str) = ("div", 'product-card__img-wrap')
    product_prices: (str, str) = ("p", "product-card__price")
    product_brand_name: (str, str) = ("span", 'product-card__brand')
    product_goods_name: (str, str) = ("span", 'product-card__name')
    comments_info: (str, str) = ("span", "product-card__rating")


def scroll_down(driver):
    last_height = driver.execute_script('return document.body.scrollHeight')
    new_height = last_height + 1
    while last_height != new_height:
        driver.execute_script(f'window.scrollTo({{top: {last_height}, left: 0, behavior: "smooth"}});')
        sleep(0.5)
        last_height, new_height = new_height, driver.execute_script('return document.body.scrollHeight')


def all_prices_parsing(text: str) -> tuple:
    # Текущая и старая цена товара
    no_spaces = re.sub(r'[\s.,-]', '', text)
    split_symbol = re.search(r'\D', no_spaces)[0]

    # Решаем следующую ситуацию: ['124728', '191890', ''] -> ['124728', '191890']
    return tuple(int(price) for price in no_spaces.split(split_symbol) if price)


def parse_soup_html(card_elems):
    res = []
    for card in card_elems:
        prices = all_prices_parsing(card.find(*WildBerries.product_prices).text)
        comments_info = card.find(*WildBerries.comments_info)
        res.append({
            "url": card.find_next('a').get('href'),
            "img": f"https{card.find(*WildBerries.product_img).find('img').get('src')}",
            "current_price": min(prices),
            "old_price": max(prices),
            "brand_name": card.find(*WildBerries.product_brand_name).text,
            "goods_name": card.find(*WildBerries.product_goods_name).text,
            "reviews": float(comments_info.get('class')[-1][-1]) if comments_info else None,
            "comments": int(comments_info.find_next('span').text) if comments_info else None,
            "market": "aliexpress",
            "raiting": random.random() * 100
        })
    return res


def main(input_name: str):
    driver_executable_path = ChromeDriverManager().install()
    options = ChromeOptions()
    # options.add_argument('--headless=new')
    options.add_argument('--start-maximized')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = Chrome(driver_executable_path=driver_executable_path, options=options, version_main=110)

    start = time()
    driver.get(WildBerries.domain_url)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located(WildBerries.content))
    elem = driver.find_element(*WildBerries.search_input)

    elem.clear()
    elem.send_keys(input_name + Keys.ENTER)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(WildBerries.card_selen))

    scroll_down(driver)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    card_elems = html_soup.find_all(*WildBerries.card_bs)

    # Для отладки
    with open('html_test.html', 'w', encoding='utf-8') as file:
        file.write(BeautifulSoup(driver.page_source, 'lxml').prettify())

    res = parse_soup_html(card_elems)

    driver.close()
    # pprint(res)
    print(len(res))
    print(time() - start)  # текущий результат: ~6 секунд
    return res


main("rtx 3080")
