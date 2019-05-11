#!/usr/bin/env python
# coding: utf-8

from flask import Blueprint
from app.auxiliary.query_tools import initialProcessing


ml_handler = Blueprint('ml_handler', __name__, url_prefix="/run")


# Выполнение расчета
@ml_handler.route('/', methods=['POST'])
@initialProcessing
def run(start_time, query_id):
    pass
