from time import time

from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


input_name = "RTX 3080"


class Ozon:
    domain_url: str = "https://www.ozon.ru"
    search_input: (str, str) = (By.ID, 'searchInput')
    content_selen: (str, str) = (By.CLASS_NAME, "widget-search-result-container")
    content_bs: (str, str) = ("div", "widget-search-result-container")
    card: (str, str) = (By.CLASS_NAME, "product-card__main")
    tags: (str, str) = (By.CLASS_NAME, "search-tags__header")
    product_img: (str, str) = (By.CLASS_NAME, 'product-card__img')
    img_tag: (str, str) = (By.TAG_NAME, 'img')
    product_prices: (str, str) = (By.CLASS_NAME, "product-card__price")
    product_brand_name: (str, str) = (By.CLASS_NAME, 'brand-name')
    product_goods_name: (str, str) = (By.CLASS_NAME, 'goods-name')


driver_executable_path = ChromeDriverManager().install()
options = ChromeOptions()
# options.page_load_strategy = 'eager'  # ждем лишь загрузки DOM страницы
options.add_argument('--start-maximized')
driver = Chrome(driver_executable_path=driver_executable_path, options=options)

start = time()
driver.get(Ozon.domain_url)

elem = driver.find_element(By.TAG_NAME, "input")  # ищем первый input

elem.clear()
elem.send_keys(input_name + Keys.ENTER)

WebDriverWait(driver, 10).until(ec.presence_of_element_located(Ozon.content_selen))

html_soup = BeautifulSoup(driver.page_source, features="lxml")
card_elems = html_soup.find(*Ozon.content_bs).find_next("div")

# Для отладки
with open('html_test.html', 'w', encoding='utf-8') as file:
    file.write(BeautifulSoup(driver.page_source, 'lxml').prettify())

driver.close()
print(time() - start)

# html_soup.find(*Ozon.content_bs).find_next("div").find_all("div", recursive=False)[4].find_all("div", recursive=False)
