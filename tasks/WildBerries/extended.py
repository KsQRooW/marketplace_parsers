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

    clean_url = url.replace('/detail.aspx', '')

    driver.get(url)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "product-params__table")))
    html_soup = BeautifulSoup(driver.page_source, features="lxml")

    imgs_content_tags = html_soup.find("ul", "swiper-wrapper").find_all("div", "slide__content")
    img_urls = [img.get('src') for imgs_content in imgs_content_tags if (img := imgs_content.find("img"))]
    final_price = int(re.sub(r'[\D\s.,-]', '', html_soup.find("ins", "price-block__final-price").text))

    names_info = html_soup.find("div", "product-page__header")
    brand_name = names_info.find('span').text
    product_name = names_info.find('h1').text


    params = {}
    all_tr = html_soup.find_all("tr", "product-params__row")
    for tr in all_tr:
        params[tr.find_next('span').text] = tr.find_next('span').find_next('span').find_next('span').text

    driver.get(f"{clean_url}/feedbacks")

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "comments__list")))

    scroll_down(driver, delay=0.5)

    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    all_text = '. '.join(p.text for p in html_soup.find_all("p", "feedback__text"))

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


# from pprint import pprint
# pprint(parse_extend("https://www.wildberries.ru/catalog/39643917/detail.aspx"))