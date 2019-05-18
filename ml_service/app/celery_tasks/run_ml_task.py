#!/usr/bin/env python
# coding: utf-8

import os
import time
import importlib.util
from cel_api import celery_api
from app.database import db
from app.auxiliary.celery_tools import celeryLogFailAndEmail, celeryLogSuccessAndEmail, \
                                       getDateAndTimeByKey, addWhereToExpression
from app.auxiliary.transaction import transaction
from app.db_entities.results_view import Results
from app.logger import Logger


@celery_api.task(bind=True)
def ml_task_runner(self, parameters):
    start_time = time.perf_counter()

    self.update_state(state='PROGRESS',
                      meta={'current': 1, 'total': 100,
                            'status': 'Importing started.'})

    importlib.invalidate_caches()

    try:
        model_spec = importlib.util.spec_from_file_location('Model', parameters.get('model'))
        class_model = importlib.util.module_from_spec(model_spec)
        model_spec.loader.exec_module(class_model)
        model = class_model.Model()
    except (ImportError, AttributeError, TypeError) as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Bad preprocessor file.")

    try:
        prep_spec = importlib.util.spec_from_file_location('Preprocessor', parameters.get('preprocessor'))
        class_prep = importlib.util.module_from_spec(prep_spec)
        prep_spec.loader.exec_module(class_prep)
        prep = class_prep.Preprocessor()
    except (ImportError, AttributeError, TypeError) as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Bad preprocessor file.")

    self.update_state(state='PROGRESS',
                      meta={'current': 3, 'total': 100,
                            'status': 'Importing finished. Receiving cursor.'})

    # взять курсор
    dt_key = 'From'
    (dateFrom, timeFrom) = getDateAndTimeByKey(parameters, dt_key, self.request.id)

    dt_key = 'To'
    (dateTo, timeTo) = getDateAndTimeByKey(parameters, dt_key, self.request.id)

    tickers = parameters.get('ticker')

    if tickers and not isinstance(tickers, list):
        tickers = [tickers]

    expr = "SELECT * FROM Data"

    if tickers or dateFrom or timeFrom or dateTo or timeTo:
        expr = addWhereToExpression(expr, tickers, dateFrom, timeFrom, dateTo, timeTo)
        if not expr:
            celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'),
                                  "CombineError(Not an exception)")
            raise RuntimeError("Bad structure of finder fields.")

    expr = " ".join([expr, "ORDER BY date DESC, time DESC;"])

    Logger.debug(expr)

    from app.fl_app import application

    with application.app_context():
        try:
            cursor = db.engine.raw_connection().cursor()
            cursor.execute(expr)
        except Exception as ex:
            celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
            raise RuntimeError("Exception during getting cursor from database.")

    self.update_state(state='PROGRESS',
                      meta={'current': 10, 'total': 100,
                            'status': 'Cursor has been received. Preprocessing started.'})

    try:
        data = prep.preprocess(cursor)
    except (AttributeError, TypeError) as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Bad preprocessor file.")
    except Exception as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Exception in runtime of preprocessing.")

    self.update_state(state='PROGRESS',
                      meta={'current': 35, 'total': 100,
                            'status': 'Preprocessing finished. Loading data started.'})

    try:
        model.load(parameters.get('resource'))
    except (AttributeError, TypeError) as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Bad model file.")
    except Exception as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Exception in runtime of loading data.")

    self.update_state(state='PROGRESS',
                      meta={'current': 65, 'total': 100,
                            'status': 'Loading data finished. Predicting started.'})

    try:
        prediction = model.predict(data)
    except (AttributeError, TypeError) as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Bad model file.")
    except Exception as ex:
        celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
        raise RuntimeError("Exception in runtime of predicting.")

    self.update_state(state='PROGRESS',
                      meta={'current': 93, 'total': 100,
                            'status': 'Prediction made. Adding it to database.'})

    # Вставка в db
    with application.app_context():
        try:
            with transaction():
                full_result = Results()
                full_result.model = os.path.basename(parameters.get('model'))
                full_result.preprocessor = os.path.basename(parameters.get('preprocessor'))
                full_result.resource = os.path.basename(parameters.get('resource'))
                full_result.personEmail = parameters.get('personEmail')
                for key in prediction.keys():
                    try:
                        setattr(full_result, key, prediction.get(key))
                    except (AttributeError, TypeError):
                        Logger.warn(f"Wrong attribute or type  in predicton. "
                                    f"Continue running task. task_id: {self.request.id} \n"
                                    f"key=<{key}>; value=<{prediction.get(key)}>")
                db.session.add(full_result)
        except Exception as ex:
            celeryLogFailAndEmail(self.request.id, start_time, parameters.get('personEmail'), type(ex).__name__)
            raise RuntimeError("Exception during insertion into database.")

        db.session.commit()

    self.update_state(state='PROGRESS',
                      meta={'current': 97, 'total': 100,
                            'status': 'Inserting to database finished. Sending mail'})

    # Отправка сообщения на почту
    celeryLogSuccessAndEmail(self.request.id, start_time, parameters.get('personEmail'), prediction)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': prediction}
