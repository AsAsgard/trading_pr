#!/usr/bin/env python
# coding: utf-8

import os
import importlib
import importlib.util
from flask import Blueprint
from app.auxiliary.query_tools import initialProcessing
from app.auxiliary.query_tools import logFail, logSuccess
from flask import request, abort, jsonify
from werkzeug.exceptions import HTTPException
from app.database import db
from app.db_entities.results_view import Results
from app.queries.resources_handler import res_parameters
from app.queries.preprocessors_handler import prep_parameters
from app.queries.models_handler import model_parameters
from app.celery_tasks.run_ml_task import ml_task_runner

ml_handler = Blueprint('ml_handler', __name__, url_prefix="/predictions")


# Выполнение расчета
@ml_handler.route('/run', methods=['POST'])
@initialProcessing
def run_prediction(start_time, query_id):

    request_data = request.get_json()

    if not request_data.get('model'):
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Specify {model_parameters.get('entity')} in the request.")

    if not request_data.get('preprocessor'):
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Specify {prep_parameters.get('entity')} in the request.")

    if not request_data.get('resource'):
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Specify {res_parameters.get('entity')} in the request.")

    model_path = os.path.join(model_parameters.get('folder'), request_data.get('model'))
    if not os.path.isfile(model_path):
        code = 404
        logFail(query_id, start_time, code)
        abort(code, f"No {model_parameters.get('entity')} with this filename.")

    prep_path = os.path.join(prep_parameters.get('folder'), request_data.get('preprocessor'))
    if not os.path.isfile(prep_path):
        code = 404
        logFail(query_id, start_time, code)
        abort(code, f"No {prep_parameters.get('entity')} with this filename.")

    res_path = os.path.join(res_parameters.get('folder'), request_data.get('resource'))
    if not os.path.isfile(res_path):
        code = 404
        logFail(query_id, start_time, code)
        abort(code, f"No {res_parameters.get('entity')} with this filename.")

    importlib.invalidate_caches()

    try:
        model_spec = importlib.util.spec_from_file_location('Model', model_path)
        class_model = importlib.util.module_from_spec(model_spec)
        model_spec.loader.exec_module(class_model)
        model = class_model.Model()
    except (ImportError, AttributeError, TypeError):
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Bad model file.")

    try:
        prep_spec = importlib.util.spec_from_file_location('Preprocessor', prep_path)
        class_prep = importlib.util.module_from_spec(prep_spec)
        prep_spec.loader.exec_module(class_prep)
        prep = class_prep.Preprocessor()
    except (ImportError, AttributeError, TypeError):
        code = 400
        logFail(query_id, start_time, code)
        abort(code, f"Bad preprocessor file.")

    parameters = {
        'model': model_path,
        'preprocessor': prep_path,
        'resource': res_path,
        'personEmail': request.headers.get('email')
    }

    # взять курсор
    cursor = None

    # в Celery
    task = ml_task_runner.apply_async(args=[prep_path, model_path, res_path, cursor, parameters])
    # --------------------------

    logSuccess(query_id, start_time)

    return jsonify(task_id=task.id), 202


@ml_handler.route('/status/<task_id>', methods=['GET'])
@initialProcessing
def check_status(task_id, start_time, query_id):
    from app.celery_tasks.run_ml_task import ml_task_runner
    task = ml_task_runner.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 100,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 100),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 100,
            'total': 100,
            'status': str(task.info),  # this is the exception raised
        }
    logSuccess(query_id, start_time)
    return jsonify(response), 200


# Список результатов для пользователя
@ml_handler.route('/list', methods=['GET'])
@initialProcessing
def result_list(start_time, query_id):
    try:
        # Соединение таблиц и получение информации
        personinf = db.session.query(Results)\
                    .filter_by(personid=request.headers.get('personid'))\
                    .order_by(Results.datetime)\
                    .all()
    except HTTPException as ex:
        logFail(query_id, start_time, ex.code)
        raise

    logSuccess(query_id, start_time)

    if not personinf:
        return jsonify("Empty set"), 200

    return jsonify(personinf), 200
