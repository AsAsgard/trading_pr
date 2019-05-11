#!/usr/bin/env python
# coding: utf-8

from flask import Blueprint
from flask import request, abort, jsonify
from sqlalchemy import func
from app.database import db
from app.auxiliary.transaction import transaction
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.auxiliary.file_handlers.file_handler import handleFile
from werkzeug.exceptions import HTTPException
from app.auxiliary.query_tools import initialProcessing, logFail, logSuccess

data_handler = Blueprint('data_handler', __name__, url_prefix="/data")


# Загрузка файла
@data_handler.route('/', methods=['POST'])
@initialProcessing
def upload_file(start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    if not isinstance(request.files['file'].filename, str) or len(request.files['file'].filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    file = Files(filename=request.files['file'].filename)
    try:
        with transaction():
            with transaction():
                db.session.add(file)
            db.session.flush()
            handleFile(file.fileid, request.files['file'])
    except HTTPException as ex:
        db.session.query(Files).filter_by(fileid=file.fileid).delete()
        logFail(query_id, start_time, ex.code)
        raise

    db.session.commit()

    logSuccess(query_id, start_time)

    return jsonify(fileid=file.fileid), 200


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
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    if not isinstance(request.files['file'].filename, str) or len(request.files['file'].filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    # Изменение в бд
    try:
        with transaction():
            db.session.query(Data).filter_by(fileid=fileid).delete()
            handleFile(fileid, request.files['file'])
            Files.query.filter_by(fileid=fileid).update({'filename': request.files['file'].filename})
    except HTTPException as ex:
        db.session.rollback()
        logFail(query_id, start_time, ex.code)
        raise

    db.session.commit()

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
        abort(code, "Bad request body. Expected .csv file with key 'file' and correct filename in request body.")

    if not isinstance(request.files['file'].filename, str) or len(request.files['file'].filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    # Изменение в бд
    try:
        with transaction():
            handleFile(fileid, request.files['file'])
            Files.query.filter_by(fileid=fileid).update({'filename': request.files['file'].filename})
    except HTTPException as ex:
        db.session.rollback()
        logFail(query_id, start_time, ex.code)
        raise

    db.session.commit()

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
