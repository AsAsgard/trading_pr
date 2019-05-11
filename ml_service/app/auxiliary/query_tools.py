#!/usr/bin/env python
# coding: utf-8

import time
from functools import wraps
from threading import Lock
from flask import request
from app.logger import Logger

query_counter = 0
lock = Lock()


# вычисление данных запроса
def initialProcessing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global query_counter
        start_time = time.perf_counter()
        with lock:
            query_counter += 1
            query_id = query_counter
        Logger.info(f'Query: query_id: <{query_id}> method: <{request.method}>; path=<{request.path}>')
        return func(start_time=start_time, query_id=query_id, *args, **kwargs)
    return wrapper


# Вычисление времни выполнения в мс
def calc_time(start_time):
    return (time.perf_counter() - start_time) * 1000


def logFail(query_id, start_time, code):
    Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                f"time: <{calc_time(start_time)} ms>")


def logSuccess(query_id, start_time):
    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")
