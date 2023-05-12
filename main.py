from celery import group
from fastapi import FastAPI
import uvicorn
from time import time

from tasks.base import ozon_run, wb_run, ali_run


app = FastAPI()


@app.get("/search")
def route(input_name: str):
    start = time()
    task_ozon = ozon_run.s(input_name)
    task_wb = wb_run.s(input_name)
    task_ali = ali_run.s(input_name)
    res = group(task_ozon, task_wb, task_ali)().get()
    print(time() - start)
    return res


""" Запуск приложения (аналогично uvicorn main:app --reload) """

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', log_level="info", port=8888)
