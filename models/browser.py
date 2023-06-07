from time import sleep

from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    try:
        driver_executable_path = ChromeDriverManager().install()
    except PermissionError:
        driver_executable_path = ChromeDriverManager().install()
    options = ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = Chrome(driver_executable_path=driver_executable_path, options=options)
    return browser


def scroll_down(driver: Chrome, delay: int | float = 1):
    """
    Плавно скролим страницу с помощью JS

    :param driver: Экземпляр запущенного веб-драйвера (формально - браузера)
    :param delay:
    """
    last_height = driver.execute_script('return document.body.scrollHeight')
    new_height = last_height + 1
    while last_height != new_height:
        driver.execute_script(f'window.scrollTo({{top: {last_height}, left: 0, behavior: "smooth"}});')
        sleep(delay)
        last_height, new_height = new_height, driver.execute_script('return document.body.scrollHeight')
