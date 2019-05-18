#!/usr/bin/env python
# coding: utf-8

import uuid
from flask import Blueprint
from flask import request, abort, jsonify
from sqlalchemy import func
from app.database import db
from app.auxiliary.transaction import transaction
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from werkzeug.exceptions import HTTPException
from app.auxiliary.query_tools import initialProcessing, logFail, logSuccess
from app.celery_tasks.upload_file_data import post_task, put_task, patch_task

data_handler = Blueprint('data_handler', __name__, url_prefix="/data")


# Загрузка файла
@data_handler.route('/', methods=['POST'])
@initialProcessing
def upload_file(start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Bad request body. Expected file with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    filepath = f"/tmp/{uuid.uuid4()}"

    request.files['file'].save(filepath)

    post_params = {
        'filename': filename,
        'filepath': filepath,
        'personEmail': request.headers.get('email')
    }

    task = post_task.apply_async(args=[post_params])

    logSuccess(query_id, start_time)

    return jsonify(task_id=task.id), 202


# Изменение файла
@data_handler.route('/<fileid>', methods=['PUT'])
@initialProcessing
def change_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "No file with such fileID in database.")

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Bad request body. Expected file with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    filepath = f"/tmp/{uuid.uuid4()}"

    request.files['file'].save(filepath)

    put_params = {
        'filename': filename,
        'filepath': filepath,
        'fileid': fileid,
        'personEmail': request.headers.get('email')
    }

    # Изменение в бд
    put_task.apply_async(args=[put_params])

    logSuccess(query_id, start_time)

    return '', 204


# Добавление в файл информации
@data_handler.route('/<fileid>', methods=['PATCH'])
@initialProcessing
def update_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        logFail(query_id, start_time, code)
        abort(code, "No file with such fileID in database.")

    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Bad request body. Expected file with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    filepath = f"/tmp/{uuid.uuid4()}"

    request.files['file'].save(filepath)

    patch_params = {
        'filename': filename,
        'filepath': filepath,
        'fileid': fileid,
        'personEmail': request.headers.get('email')
    }

    # Изменение в бд
    patch_task.apply_async(args=[patch_params])

    logSuccess(query_id, start_time)

    return '', 204


# Получение информации о загруженном файле пользователя
@data_handler.route('/<fileid>', methods=['GET'])
@initialProcessing
def file_info(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        logFail(query_id, start_time, code)
        abort(code, "No file with such fileID in database.")

    try:
        # Соединение таблиц и получение информации
        fileinf = db.session.query(Files, func.count(Data.fileid).label('count_rows'))\
            .join(Files.data)\
            .group_by(Files.fileid)\
            .having(Files.fileid == fileid)\
            .first()
    except HTTPException as ex:
        logFail(query_id, start_time, ex.code)
        raise

    logSuccess(query_id, start_time)

    return jsonify(
        fileid=int(fileid),
        filename=fileinf[0].filename,
        first_download=fileinf[0].first_download,
        last_download=fileinf[0].last_download,
        data_count=fileinf.count_rows
    ), 200


# список файлов с количеством их записей
@data_handler.route('/list', methods=['GET'])
@initialProcessing
def files_list(start_time, query_id):
    if not Files.query.all():
        logSuccess(query_id, start_time)
        return jsonify("Empty set.")

    try:
        # Соединение таблиц и получение информации
        fileinf = db.session.query(Files, func.count(Data.fileid).label('count_rows'))\
            .join(Files.data)\
            .group_by(Files.fileid)\
            .all()
    except HTTPException as ex:
        logFail(query_id, start_time, ex.code)
        raise

    logSuccess(query_id, start_time)

    return jsonify([
        {
            "fileid": fileinf[i][0].fileid,
            "filename": fileinf[i][0].filename,
            "count_rows": fileinf[i].count_rows,
        }
        for i in range(0, len(fileinf))
    ]), 200


# Удаление файла
@data_handler.route('/<fileid>', methods=['DELETE'])
@initialProcessing
def delete_file(fileid, start_time, query_id):
    if not Files.query.filter_by(fileid=fileid).all():
        code = 404
        logFail(query_id, start_time, code)
        abort(code, "No file with such fileID in database.")

    # Удаление из бд
    try:
        with transaction():
            db.session.query(Data).filter_by(fileid=fileid).delete(synchronize_session="fetch")
            db.session.query(Files).filter_by(fileid=fileid).delete(synchronize_session="fetch")
    except HTTPException as ex:
        logFail(query_id, start_time, ex.code)
        raise

    db.session.commit()

    logSuccess(query_id, start_time)

    return '', 204
