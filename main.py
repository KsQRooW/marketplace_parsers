from typing import Annotated

from celery import group
from fastapi import FastAPI, Query
import uvicorn

from tasks.base import ozon_run, wb_run, ali_run, wb_extended_run, ozon_extended_run, ali_extended_run


app = FastAPI()
MARKETPLACE_JOBS = {
        "wildberries": {
            "search": wb_run,
            "extended": wb_extended_run
        },
        "ozon": {
            "search": ozon_run,
            "extended": ozon_extended_run
        },
        "aliexpress": {
            "search": ali_run,
            "extended": ali_extended_run
        },
    }



@app.get("/search")
def route(input_name: str, marketplaces: Annotated[list[str], Query()] = ("wildberries", "ozon", "aliexpress")):
    tasks = [MARKETPLACE_JOBS[marketplace]["search"].s(input_name) for marketplace in marketplaces]
    tasks_res = group(*tasks)().get()
    response = []
    for res in tasks_res:
        if res is not None:
            response.extend(res)
    return response


@app.get("/extended/{marketplace}/{url}")
def extended_params(marketplace: str, url: str):
    return MARKETPLACE_JOBS[marketplace]["extended"].delay(url).get()



if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', log_level="info", port=8888)
