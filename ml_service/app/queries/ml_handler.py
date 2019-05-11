#!/usr/bin/env python
# coding: utf-8

import time
from functools import wraps
from threading import Lock
from flask import Blueprint
from flask import request, abort, jsonify
from sqlalchemy import func
from app.database import db
from app.logger import Logger
from werkzeug.exceptions import HTTPException

ml_handler = Blueprint('ml_handler', __name__, url_prefix="/run")
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


# Выполнение расчета
@ml_handler.route('/', methods=['POST'])
@initialProcessing
def run(start_time, query_id):
    pass
