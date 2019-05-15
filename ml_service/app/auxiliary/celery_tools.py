#!/usr/bin/env python
# coding: utf-8

import os
from flask_mail import Mail, Message
from app.auxiliary.query_tools import calc_time
from app.logger import Logger


def sendEmail(email, msg_body):
    from app.fl_app import application
    mail = Mail(application)
    with application.app_context():
        msg = Message('Response from Trading Project', recipients=[email])
        msg.body = msg_body
        mail.send(msg)


def celeryLogFailAndEmail(task_id, start_time, email, ex_name):
    message = f"Your request was failed. To know why - you can make a status request with your task ID: {task_id}"
    sendEmail(email, message)
    Logger.info(f"Response: Celery task failed. task_id: <{task_id}>; exc_name: <{ex_name}>; "
                f"time: <{calc_time(start_time)} ms>")


def celeryLogSuccessAndEmail(task_id, start_time, email, result):
    message = f"Your request successed! The result is:\n" \
              f"{result}"
    sendEmail(email, message)
    Logger.info(f"Response: Query successed. query_id: <{task_id}>; "
                f"time: <{calc_time(start_time)} ms>")
