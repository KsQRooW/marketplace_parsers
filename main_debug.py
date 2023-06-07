from time import time
from typing import Annotated

from fastapi import FastAPI, Query
import uvicorn

from tasks.base import main_ozon, main_wb, main_ali, parse_extend_wb, parse_extend_ozon, parse_extend_ali


app = FastAPI()

MARKETPLACE_JOBS = {
        "wildberries": {
            "search": main_wb,
            "extended": parse_extend_wb
        },
        "ozon": {
            "search": main_ozon,
            "extended": parse_extend_ozon
        },
        "aliexpress": {
            "search": main_ali,
            "extended": parse_extend_ali
        },
    }


@app.get("/search")
def route(input_name: str, marketplaces: Annotated[list[str], Query()] = ("wb", )):
    time_start = time()

    tasks_res = [MARKETPLACE_JOBS["wildberries"]["search"](input_name),
                 MARKETPLACE_JOBS["ozon"]["search"](input_name),
                 MARKETPLACE_JOBS["aliexpress"]["search"](input_name)]
    response = []
    for res in tasks_res:
        if res is not None:
            response.extend(res)

    print(f"time_end: {time() - time_start}")
    return response


@app.get("/extended/{marketplace}")
def extended_params(marketplace: str, url: str):
    return MARKETPLACE_JOBS[marketplace]["extended"](url)


if __name__ == "__main__":
    uvicorn.run("main_debug:app", host='0.0.0.0', log_level="info", port=8888)
