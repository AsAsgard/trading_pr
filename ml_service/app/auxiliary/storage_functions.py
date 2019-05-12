#!/usr/bin/env python
# coding: utf-8

import os
from flask import request, abort, jsonify
from app.auxiliary.query_tools import initialProcessing, logFail, logSuccess


# Загрузка компонента
@initialProcessing
def storage_upload(parameters, start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Bad request body. Expected {parameters.get('extension')} file "
                    f"with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    abs_path_filename = os.path.join(parameters.get('folder'), filename)
    if os.path.isfile(abs_path_filename):
        code = 409
        logFail(query_id, start_time, code)
        abort(code, f"The {parameters.get('entity')} with the same filename already exists.")

    request.files['file'].save(abs_path_filename)

    logSuccess(query_id, start_time)

    return '', 204


# Замена компонента
@initialProcessing
def storage_replace(parameters, start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Bad request body. Expected {parameters.get('extension')} file "
        f"with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    abs_path_filename = os.path.join(parameters.get('folder'), filename)
    if not os.path.isfile(abs_path_filename):
        code = 404
        logFail(query_id, start_time, code)
        abort(code, f"No {parameters.get('entity')} with this filename.")

    os.remove(abs_path_filename)

    request.files['file'].save(abs_path_filename)

    logSuccess(query_id, start_time)

    return '', 204


# Загрузка или изменение компонента
@initialProcessing
def storage_insert(parameters, start_time, query_id):
    if 'file' not in request.files or not request.files['file'].filename:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Bad request body. Expected {parameters.get('extension')} file "
        f"with key 'file' and correct filename in request body.")

    filename = request.files['file'].filename \
        if not request.headers.get('filename') \
        else request.headers.get('filename')

    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    abs_path_filename = os.path.join(parameters.get('folder'), filename)
    if os.path.isfile(abs_path_filename):
        os.remove(abs_path_filename)

    request.files['file'].save(abs_path_filename)

    logSuccess(query_id, start_time)

    return '', 204


# Список загруженных компонентов
@initialProcessing
def storage_list(parameters, start_time, query_id):
    files = next(os.walk(parameters.get('folder')))[2]

    logSuccess(query_id, start_time)

    if not files:
        return jsonify("Empty set"), 200

    return jsonify(files), 200


# Удаление компонента
@initialProcessing
def storage_delete(parameters, filename, start_time, query_id):
    if not isinstance(filename, str) or len(filename) > 99:
        code = 400
        logFail(query_id, start_time, code)
        abort(code, "Too long or bad filename.")

    abs_path_filename = os.path.join(parameters.get('folder'), filename)
    if not os.path.isfile(abs_path_filename):
        code = 404
        logFail(query_id, start_time, code)
        abort(code, f"No {parameters.get('entity')} with this filename.")

    os.remove(abs_path_filename)

    logSuccess(query_id, start_time)

    return '', 204
