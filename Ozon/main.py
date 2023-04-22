import re
from time import time, sleep
from pprint import pprint

from bs4 import BeautifulSoup, Tag
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


input_name = "RTX 3080"
input_name2 = "чашка"


class Ozon:
    domain_url: str = "https://www.ozon.ru"
    search_input: (str, str) = (By.TAG_NAME, "input")
    content_selen: (str, str) = (By.CLASS_NAME, "widget-search-result-container")
    content_bs: (str, str) = ("div", "widget-search-result-container")
    card: (str, str) = (By.CLASS_NAME, "product-card__main")
    tags: (str, str) = (By.CLASS_NAME, "search-tags__header")
    product_img: (str, str) = (By.CLASS_NAME, 'product-card__img')


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
    split_symbol = re.search(r'\D+', no_spaces)[0]

    # Решаем следующую ситуацию: ['124728', '191890', ''] -> ['124728', '191890']
    return tuple(int(price) for price in no_spaces.split(split_symbol) if price)


def comments_reviews_parsing(spans: list[Tag]):
    reviews = comments = None
    for span in spans:
        val = span.text
        clear_val = re.sub(r'\s|[^a-zA-Z0-9_.,]', '', val)
        print(val, clear_val)
        if clear_val and not re.findall(r'[^0-9.,]', clear_val):
            if re.search(r'[.,]', clear_val):
                reviews = float(clear_val)
            else:
                comments = int(clear_val)
    return reviews, comments


def parse_soup_html_v1(card_elems):
    """ Парсинг карточек товаров, когда они располагаются горизонтальными плашками """
    res = []
    for card in card_elems:
        card_divs = card.find_all('div', recursive=False)

        comments_info = card_divs[1].find('div').find_all('div', recursive=False)
        if comments_info:
            comments_info = comments_info[-1].find_all('span', recursive=False)
        else:
            comments_info = []
        reviews, comments = comments_reviews_parsing(comments_info)

        prices_tag = card_divs[2].find_next('span').text
        if len(re.findall('[^0-9\s]', prices_tag)) > len(re.findall('[0-9]', prices_tag)):
            prices_tag = card_divs[2].find_next('div').text
        prices = all_prices_parsing(prices_tag)

        res.append({
            "url": card.find('a').get('href'),
            "img": card.find('img').get('src'),
            "current_price": min(prices),
            "old_price": max(prices),
            "brand_name": None,  # TODO: подумать, что сюда поставить
            "goods_name": card_divs[1].find_next('span').text,
            "reviews": reviews,
            "comments": comments
        })
    return res


def parse_soup_html_v2(card_elems):
    """ Парсинг карточек товаров, когда они располагаются сеткой """
    res = []
    for card in card_elems:
        card_divs = card.find_all('div', recursive=False)

        comments_info = card_divs[0].find_all('div', recursive=False)[-2].find_all('span', recursive=False)
        reviews, comments = comments_reviews_parsing(comments_info)

        prices_tag = card_divs[0].find_all('div', recursive=False)[0].text
        prices = all_prices_parsing(prices_tag)

        res.append({
            "url": card.find('a').get('href'),
            "img": card.find('img').get('src'),
            "current_price": min(prices),
            "old_price": max(prices),
            "brand_name": None,  # TODO: подумать, что сюда поставить
            "goods_name": card_divs[0].find_next('a').text,
            "reviews": reviews,
            "comments": comments
        })
    return res


def main():
    driver_executable_path = ChromeDriverManager().install()
    options = ChromeOptions()
    # options.page_load_strategy = 'eager'  # ждем лишь загрузки DOM страницы
    options.add_argument('--start-maximized')
    driver = Chrome(driver_executable_path=driver_executable_path, options=options)

    start = time()
    driver.get(Ozon.domain_url)

    elem = driver.find_element(*Ozon.search_input)  # ищем первый input

    elem.clear()
    elem.send_keys(input_name + Keys.ENTER)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located(Ozon.content_selen))

    scroll_down(driver)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    card_elems = html_soup.find(*Ozon.content_bs).find_next("div").find_all("div", recursive=False)

    if len(card_elems[0].find_all('div', recursive=False)) == 4:
        res = parse_soup_html_v1(card_elems)
    else:
        res = parse_soup_html_v2(card_elems)

    # Для отладки
    with open('html_test.html', 'w', encoding='utf-8') as file:
        file.write(BeautifulSoup(driver.page_source, 'lxml').prettify())

    driver.close()
    pprint(res)
    print(len(res))
    print(time() - start)


if __name__ == '__main__':
    main()
