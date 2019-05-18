#!/usr/bin/env python
# coding: utf-8

import os
import time
from app.database import db
from app.auxiliary.transaction import transaction
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.auxiliary.file_handlers.file_handler import handleFile
from cel_api import celery_api
from app.auxiliary.celery_tools import celeryLogFailAndEmail, celeryLogSuccessAndEmail


@celery_api.task(bind=True)
def post_task(self, post_params):
    start_time = time.perf_counter()

    from app.fl_app import application
    file = Files(filename=post_params.get('filename'))

    with application.app_context():
        try:
            with transaction():
                with transaction():
                    db.session.add(file)
                db.session.flush()
                handleFile(file.fileid, post_params.get('filepath'))
        except Exception as ex:
            db.session.query(Files).filter_by(fileid=file.fileid).delete()
            os.remove(post_params.get('filepath'))
            celeryLogFailAndEmail(self.request.id, start_time, post_params.get('personEmail'), type(ex).__name__)
            raise

        result = f"File was uploaded. Fileid: {file.fileid}"
        os.remove(post_params.get('filepath'))
        db.session.commit()

    celeryLogSuccessAndEmail(self.request.id, start_time, post_params.get('personEmail'), result)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': result}


@celery_api.task(bind=True)
def put_task(self, put_params):
    start_time = time.perf_counter()

    from app.fl_app import application
    with application.app_context():
        try:
            with transaction():
                db.session.query(Data).filter_by(fileid=put_params.get('fileid')).delete()
                handleFile(put_params.get('fileid'), put_params.get('filepath'))
                Files.query.filter_by(fileid=put_params.get('fileid'))\
                           .update({'filename': put_params.get('filename')})
        except Exception as ex:
            db.session.rollback()
            os.remove(put_params.get('filepath'))
            celeryLogFailAndEmail(self.request.id, start_time, put_params.get('personEmail'), type(ex).__name__)
            raise

        result = f"File was changed. Fileid: {put_params.get('fileid')}"
        os.remove(put_params.get('filepath'))
        db.session.commit()

    celeryLogSuccessAndEmail(self.request.id, start_time, put_params.get('personEmail'), result)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': result}


@celery_api.task(bind=True)
def patch_task(self, patch_params):
    start_time = time.perf_counter()

    from app.fl_app import application
    with application.app_context():
        try:
            with transaction():
                handleFile(patch_params.get('fileid'), patch_params.get('filepath'))
                Files.query.filter_by(fileid=patch_params.get('fileid'))\
                           .update({'filename': patch_params.get('filename')})
        except Exception as ex:
            db.session.rollback()
            os.remove(patch_params.get('filepath'))
            celeryLogFailAndEmail(self.request.id, start_time, patch_params.get('personEmail'), type(ex).__name__)
            raise

        result = f"File was changed. Fileid: {patch_params.get('fileid')}"
        os.remove(patch_params.get('filepath'))
        db.session.commit()

    celeryLogSuccessAndEmail(self.request.id, start_time, patch_params.get('personEmail'), result)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': result}
