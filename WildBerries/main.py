from pprint import pprint
import re
from time import sleep, time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


input_name = "RTX 3080"


class WildBerries:
    domain_url: str = "https://www.wildberries.ru"
    search_input: (str, str) = (By.ID, 'searchInput')
    content: (str, str) = (By.CLASS_NAME, "main-page")
    card_selen: (str, str) = (By.CLASS_NAME, "product-card__main")
    card_bs: (str, str) = ("a", "product-card__main")
    tags: (str, str) = (By.CLASS_NAME, "search-tags__header")
    product_img: (str, str) = ("div", 'product-card__img')
    product_prices: (str, str) = ("div", "product-card__price")
    product_brand_name: (str, str) = ("span", 'brand-name')
    product_goods_name: (str, str) = ("span", 'goods-name')


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
        res.append({
            "url": card.get('href'),
            "img": card.find(*WildBerries.product_img).find('img').get('src'),
            "current_price": min(prices),
            "old_price": max(prices),
            "brand_name": card.find(*WildBerries.product_brand_name).text,
            "goods_name": card.find(*WildBerries.product_goods_name).text
        })
    return res


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)

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

    # # Для отладки
    # with open('html_test.html', 'w', encoding='utf-8') as file:
    #     file.write(BeautifulSoup(driver.page_source, 'lxml').prettify())

    res = parse_soup_html(card_elems)

    driver.close()
    pprint(res)
    print(len(res))
    print(time() - start)  # текущий результат: ~6 секунд


if __name__ == '__main__':
    main()
