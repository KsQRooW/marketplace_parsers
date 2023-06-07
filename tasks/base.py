from celery import Celery
from celery.signals import task_prerun, task_postrun

from .aliexpress.main import main as main_ali
from .aliexpress.extended import parse_extend as parse_extend_ali
from .ozon.main import main as main_ozon
from .ozon.extended import parse_extend as parse_extend_ozon
from .summarizator.main import summarize
from .translator.main import translate
from .wildberries.main import main as main_wb
from .wildberries.extended import parse_extend as parse_extend_wb
from models.browser import get_driver


app = Celery('base', broker='redis://redis:6379/0', backend='redis://redis:6379/1')

app.conf.task_track_started = True
app.conf.task_ignore_result = False

app.conf.result_backend_transport_options = {
    'retry_policy': {
       'timeout': 5.0
    }
}


@task_prerun.connect
def start_browser(task, **kwargs):
    """ Инициализация браузера """
    task.driver = get_driver()


@task_postrun.connect
def close_browser(task, **kwargs):
    """ Закрытие браузера """
    task.close()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.task(bind=True, name="translate", queue="translate",
          autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def translate_run(self, text, source="ru", target="en"):
    return translate(self.driver, text, source=source, target=target)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.task(name="summarize", queue="summarize", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def summarize_run(text):
    return summarize(text)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.task(bind=True, name="ozon", queue="ozon", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def ozon_run(self, input_name: str):
    return main_ozon(input_name, self.driver)


@app.task(bind=True, name="wb", queue="wb", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def wb_run(self, input_name: str):
    return main_wb(input_name, self.driver)


@app.task(bind=True, name="ali", queue="ali", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def ali_run(self, input_name: str):
    return main_ali(input_name, self.driver)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.task(bind=True, name="ozon_extended", queue="ozon", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def ozon_extended_run(self, url: str):
    return parse_extend_ozon(self.driver, url)


@app.task(bind=True, name="wb_extended", queue="wb", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def wb_extended_run(self, url: str):
    return parse_extend_wb(self.driver, url)


@app.task(bind=True, name="ali_extended", queue="ali", autoretry_for=(Exception,), max_retries=3, default_retry_delay=1)
def ali_extended_run(self, url: str):
    return parse_extend_ali(self.driver, url)
