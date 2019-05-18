#!/usr/bin/env python
# coding: utf-8

from celery import Celery
from appconfig import getConfig
from app.logger import Logger

Logger.info('Configuring celery...')
celery_api = Celery(broker=getConfig().CELERY_BROKER_URL)
celery_api.config_from_object(getConfig())
celery_api.autodiscover_tasks(['app.celery_tasks.run_ml_task'], force=True)
Logger.info('Celery configured')
