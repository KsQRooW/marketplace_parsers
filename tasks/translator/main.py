import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from functions.timer import timer


@timer
def translate(driver, text, source="ru", target="en"):
    driver.get(f'https://translate.google.com/?sl={source}&tl={target}')
    elem = driver.find_element(By.TAG_NAME, "textarea")

    elem.send_keys(re.sub(r'[^\x00-\x7Fа-яА-Я]', '', text) + Keys.ENTER)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "HwtZe")))

    translated_text = re.sub('[\n\t\r]', '', driver.find_element(By.CLASS_NAME, "HwtZe").text)
    return translated_text
