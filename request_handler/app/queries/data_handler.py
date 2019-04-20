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
from app.auxiliary.transaction import transaction
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.auxiliary.parser import parseAndUploadData

data_handler = Blueprint('data_handler', __name__, url_prefix="/data")
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


# Загрузка файла
@data_handler.route('/', methods=['POST'])
@initialProcessing
def upload_file(start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code)

    # Добавление в бд
    file = Files(filename=request.files['file'].filename)

    with transaction():
        Files.query.add(file)
        '''
        Данный блок находится в стадии доработки
        ----------------------------------------
        parseAndUploadData(file.fileid, request.files['file'])
        '''
    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return file.fileid, 200


# Изменение файла
@data_handler.route('/<fileid>', methods=['PUT'])
@initialProcessing
def change_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code)

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code)

    # Изменение в бд
    with transaction():
        Data.query.filter_by(fileid=fileid).delete()
        Files.query.filter_by(fileid=fileid).update({'filename': request.files['file'].filename})
        '''
        Данный блок находится в стадии доработки
        ----------------------------------------
        parseAndUploadData(fileid, request.files['file'])
        '''

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return '', 204


# Получение информации о загруженном файле пользователя
@data_handler.route('/<fileid>', methods=['GET'])
@initialProcessing
def file_info(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code)

    '''
    Данный блок находится в стадии доработки
    ----------------------------------------

    # Соединение таблиц и получение информации
    fileinf = db.session.query(Files, func.count(Data.fileid).label('count_rows'))\
        .join(Files.data)\
        .group_by(Files.fileid)\
        .having(Files.fileid == fileid)\
        .first()

    return jsonify(
        fileid=fileid,
        filename=fileinf.filename,
        first_download=fileinf.first_download,
        last_download=fileinf.last_download,
        data_count=fileinf.count_rows
    ), 200
    '''

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return "Response", 200


# Удаление файла
@data_handler.route('/<fileid>', methods=['DELETE'])
@initialProcessing
def delete_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code)

    # Удаление из бд
    with transaction():
        '''
        Данный блок находится в стадии доработки
        ----------------------------------------
        Data.query.filter_by(fileid=fileid).delete()
        '''
        Files.query.filter_by(fileid=fileid).delete()

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return '', 204
