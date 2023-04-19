from pprint import pprint
import re
from time import sleep, time

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


input_name = "RTX 3080"


class AliExpress:
    domain_url: str = "https://aliexpress.ru"
    pure_name: str = "aliexpress.ru"
    search_input: (str, str) = (By.ID, 'searchInput')
    content: (str, str) = (By.CSS_SELECTOR, 'div[class^="product-snippet_ProductSnippet__content__"')
    card_selen: (str, str) = (By.CSS_SELECTOR, 'div[class^="product-snippet_ProductSnippet__content__"')
    card_bs: dict = {"class_": re.compile('product-snippet_ProductSnippet__content__')}
    product_img: dict = {"class_": re.compile('gallery_Gallery__image__')}
    product_brand_name: dict = {"class_": re.compile('product-snippet_ProductSnippet__shop__')}
    product_goods_name: dict = {"class_": re.compile('product-snippet_ProductSnippet__name__')}
    current_price: dict = {"class_": re.compile('snow-price_SnowPrice__mainM__')}
    old_price: dict = {"class_": re.compile('snow-price_SnowPrice__secondPrice__')}


def scroll_down(driver):
    last_height = driver.execute_script('return document.body.scrollHeight')
    new_height = last_height + 1
    while last_height != new_height:
        driver.execute_script(f'window.scrollTo({{top: {last_height}, left: 0, behavior: "smooth"}});')
        sleep(0.5)
        last_height, new_height = new_height, driver.execute_script('return document.body.scrollHeight')


def clean_url(raw_url: str) -> str:
    """Очистить ссылки от начальных '/' """
    if raw_url.startswith('/'):
        return clean_url(raw_url[1:])
    return raw_url


def parse_url(html_part: Tag) -> str:
    """Ссылка на товар"""
    item_url = html_part.find('a').get('href')
    item_url = clean_url(item_url)
    if item_url.startswith(AliExpress.domain_url):
        return item_url
    if item_url.startswith(AliExpress.pure_name):
        return 'https://' + item_url
    # Если ссылки относительные (/item/1005004065604805.html?sku_id=12000027923647408)
    # return AliExpress.domain_url + '/' + item_url[1:] if item_url[0] == '/' else item_url  # Оставить 1 слэш
    return AliExpress.domain_url + '/' + clean_url(item_url)


def parse_img_url(html_part: Tag) -> str:
    """Изображение товара"""
    # Берем первую картинку из карусели
    img_url = html_part.find(**AliExpress.product_img).get('src')
    if img_url and len(img_url) > 2 and img_url[:2] == '//':
        img_url = img_url[2:]
    return img_url


def parse_brand_name(html_part: Tag):
    """Название бренда"""
    brand_name = html_part.find(**AliExpress.product_brand_name)
    brand_name = brand_name.text if brand_name else None
    return brand_name


def parse_item_name(html_part: Tag):
    """Название товара"""
    item_name = html_part.find_next(**AliExpress.product_goods_name)
    item_name = item_name.text if item_name else None
    return item_name


def parse_current_price(html_part: Tag):
    """Текущая цена товара"""
    current_price_raw = html_part.find(AliExpress.current_price)
    current_price_raw = current_price_raw.text if current_price_raw else None
    current_price = current_price_raw  # TODO обработать цену
    return current_price


def parse_old_price(html_part: Tag):
    """Старая цена товара"""
    old_price_raw = html_part.find(**AliExpress.old_price)
    old_price_raw = old_price_raw.text if old_price_raw else None
    old_price = old_price_raw  # TODO обработать цену
    return old_price


def parse_soup_html(card_elems):
    res = []
    for card in card_elems:

        res.append({
            "url": parse_url(card),
            "img": parse_img_url(card),
            "current_price": parse_current_price(card),
            "old_price": parse_old_price(card),
            "brand_name": parse_brand_name(card),
            "goods_name": parse_item_name(card)
        })
    return res


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    start = time()
    driver.get(AliExpress.domain_url)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located(AliExpress.content))
    elem = driver.find_element(*AliExpress.search_input)

    elem.clear()
    elem.send_keys(input_name + Keys.ENTER)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(AliExpress.card_selen))

    scroll_down(driver)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    card_elems = html_soup.find_all(**AliExpress.card_bs)

    res = parse_soup_html(card_elems)

    driver.close()
    pprint(res)
    print(len(res))
    print(time() - start)


if __name__ == '__main__':
    main()
