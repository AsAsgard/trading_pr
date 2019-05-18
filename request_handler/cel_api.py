#!/usr/bin/env python
# coding: utf-8

from celery import Celery
from appconfig import getConfig
from app.logger import Logger

Logger.info('Configuring celery...')
celery_api = Celery(broker=getConfig().CELERY_BROKER_URL)
celery_api.config_from_object(getConfig())
celery_api.autodiscover_tasks(['app.celery_tasks.upload_file_data'], force=True)
Logger.info('Celery configured')
