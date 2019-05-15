#!/usr/bin/env python
# coding: utf-8

from celery import Celery
from fl_app import application

celery_api = Celery('ml_service', broker=application.config.get('CELERY_BROKER_URL'))
celery_api.conf.update(application.config)
