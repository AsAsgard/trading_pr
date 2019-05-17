#!/usr/bin/env python
# coding: utf-8

import os
import time
import importlib.util
from cel_api import celery_api
from app.database import db
from app.auxiliary.celery_tools import celeryLogFailAndEmail, celeryLogSuccessAndEmail
from app.auxiliary.transaction import transaction
from app.db_entities.results_view import Results


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
    cursor = None

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
    try:
        with transaction():
            full_result = Results()
            full_result.model = os.path.basename(parameters.get('model'))
            full_result.preprocessor = os.path.basename(parameters.get('preprocessor'))
            full_result.resource = os.path.basename(parameters.get('resource'))
            full_result.personEmail = parameters.get('personEmail')
            full_result.result = prediction
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

