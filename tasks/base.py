from celery import Celery

from .AliExpress.main import main as main_ali
from .Ozon.main import main as main_ozon
from .WildBerries.main import main as main_wb


app = Celery('base', broker='redis://redis:6379/0', backend='redis://redis:6379/1')

app.conf.task_track_started = True
app.conf.task_ignore_result = False

app.conf.result_backend_transport_options = {
    'retry_policy': {
       'timeout': 5.0
    }
}


@app.task(name="ozon", queue="ozon", autoretry_for=(Exception,), max_retries=5, default_retry_delay=1)
def ozon_run(input_name: str):
    return main_ozon(input_name)


@app.task(name="wb", queue="wb", autoretry_for=(Exception,), max_retries=5, default_retry_delay=1)
def wb_run(input_name: str):
    return main_wb(input_name)


@app.task(name="ali", queue="ali", autoretry_for=(Exception,), max_retries=5, default_retry_delay=1)
def ali_run(input_name: str):
    return main_ali(input_name)
