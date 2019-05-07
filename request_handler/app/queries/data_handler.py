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
from app.auxiliary.file_handlers.file_handler import handleFile
from werkzeug.exceptions import HTTPException

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
    print(f"file not in files: {'file' not in request.files}")
    if 'file' in request.files:
        print(f"not request.files['file'].filename: {not request.files['file'].filename}")
    print(request.files)

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    with transaction():
        try:
            file = Files(filename=request.files['file'].filename)
            with transaction():
                db.session.add(file)
            handleFile(file.fileid, request.files['file'])
        except HTTPException as ex:
            Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{ex.code}>; "
                        f"time: <{calc_time(start_time)} ms>")
            raise

    db.session.commit()

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return jsonify(fileid=file.fileid), 200


# Изменение файла
@data_handler.route('/<fileid>', methods=['PUT'])
@initialProcessing
def change_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "No file with such fileID in database.")

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    # Изменение в бд
    with transaction():
        try:
            Data.query.filter_by(fileid=fileid).delete()
            Files.query.filter_by(fileid=fileid).update({'filename': request.files['file'].filename})
            handleFile(fileid, request.files['file'])
        except HTTPException as ex:
            Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{ex.code}>; "
                        f"time: <{calc_time(start_time)} ms>")
            raise

    db.session.commit()

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return '', 204


# Добавление в файл информации
@data_handler.route('/<fileid>', methods=['PATCH'])
@initialProcessing
def update_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "No file with such fileID in database.")

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    # Изменение в бд
    with transaction():
        try:
            Files.query.filter_by(fileid=fileid).update({'filename': request.files['file'].filename})
            handleFile(fileid, request.files['file'])
        except HTTPException as ex:
            Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{ex.code}>; "
                        f"time: <{calc_time(start_time)} ms>")
            raise

    db.session.commit()

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
        abort(code, "No file with such fileID in database.")

    try:
        # Соединение таблиц и получение информации
        fileinf = db.session.query(Files, func.count(Data.fileid).label('count_rows'))\
            .join(Files.data)\
            .group_by(Files.fileid)\
            .having(Files.fileid == fileid)\
            .first()
    except HTTPException as ex:
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{ex.code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        raise

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return jsonify(
        fileid=int(fileid),
        filename=fileinf[0].filename,
        first_download=fileinf[0].first_download,
        last_download=fileinf[0].last_download,
        data_count=fileinf.count_rows
    ), 200


# Удаление файла
@data_handler.route('/<fileid>', methods=['DELETE'])
@initialProcessing
def delete_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{code}>; "
                    f"time: <{calc_time(start_time)} ms>")
        abort(code, "No file with such fileID in database.")

    # Удаление из бд
    with transaction():
        try:
            db.session.query(Data).filter_by(fileid=fileid).delete(synchronize_session="fetch")
            db.session.query(Files).filter_by(fileid=fileid).delete(synchronize_session="fetch")
        except HTTPException as ex:
            Logger.info(f"Response: Query failed. query_id: <{query_id}>; err_code: <{ex.code}>; "
                        f"time: <{calc_time(start_time)} ms>")
            raise

    db.session.commit()

    Logger.info(f"Response: Query successed. query_id: <{query_id}>; "
                f"time: <{calc_time(start_time)} ms>")

    return '', 204
