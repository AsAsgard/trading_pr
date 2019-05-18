#!/usr/bin/env python
# coding: utf-8

import smtplib
import datetime
from dateutil.parser import parse
from flask_mail import Mail, Message
from app.auxiliary.query_tools import calc_time
from app.logger import Logger


def sendEmail(email, msg_body):
    from app.fl_app import application
    mail = Mail(application)
    with application.app_context():
        msg = Message('Response from Trading Project', recipients=[email])
        msg.body = msg_body
        try:
            mail.send(msg)
        except (smtplib.SMTPHeloError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPSenderRefused, smtplib.SMTPDataError):
            pass


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


def getDateAndTimeByKey(parameters, dt_key, task_id):
    dateValue = None
    timeValue = None

    if parameters.get("".join(["date", dt_key])):
        try:
            dateValue = parse(parameters.get("".join(["date", dt_key]))).date()
        except ValueError:
            Logger.warn(f"Bad date format. Continue running task without it. task_id: {task_id} \n"
                        f"key=<{''.join(['date', dt_key])}>; value=<{parameters.get(''.join(['date', dt_key]))}>")

    if parameters.get("".join(["time", dt_key])):
        try:
            timeValue = parse(" ".join(["1970-01-01", parameters.get("".join(["time", dt_key]))])).time()
        except ValueError:
            Logger.warn(f"Bad time format. Continue running task without it. task_id: {task_id} \n"
                        f"key=<{''.join(['time', dt_key])}>; value=<{parameters.get(''.join(['time', dt_key]))}>")

    Logger.debug(dateValue)
    Logger.debug(timeValue)

    return (dateValue, timeValue)


def addWhereToExpression(expr, tickers, dateFrom, timeFrom, dateTo, timeTo):
    expr = " ".join([expr, "WHERE "])
    expr = "".join([expr, "("])
    if tickers:
        expr = "".join([expr, "("])
        for i in range(len(tickers)):
            if i != 0:
                expr = " ".join([expr, "OR", f"ticker='{tickers[i]}'"])
            else:
                expr = "".join([expr, f"ticker='{tickers[i]}'"])
        expr = "".join([expr, ")"])
    if dateFrom or dateTo or timeFrom or timeTo:
        expr = " ".join([expr, "AND", "("])
        needOR = False
        needAND = False

        if (dateFrom and not dateTo and timeTo) or \
           (dateTo and not dateFrom and timeFrom):
            return None

        if dateFrom and not timeFrom:
            timeFrom = datetime.time(0, 0, 0)

        if dateTo and not timeTo:
            timeTo = datetime.time(23, 59, 59)

        Logger.debug(dateFrom)
        Logger.debug(dateTo)
        Logger.debug(timeFrom)
        Logger.debug(timeTo)

        if dateFrom and dateTo:
            if dateFrom > dateTo or (dateFrom == dateTo and timeFrom > timeTo):
                return None

        # даты между
        if not dateFrom or not dateTo or dateTo != dateFrom:
            if dateFrom or dateTo:
                expr = "".join([expr, "("])

            if dateFrom:
                expr = "".join([expr, f"date>'{dateFrom.strftime('%Y-%m-%d')}'"])
                needAND = True

            if dateTo:
                if needAND:
                    expr = " ".join([expr, "AND"])
                expr = " ".join([expr, f"date<'{dateTo.strftime('%Y-%m-%d')}'"])

            if dateFrom or dateTo:
                expr = "".join([expr, ")"])
                needOR = True
                needAND = False

        # слева
        if dateFrom or timeFrom:
            if needOR:
                expr = " ".join([expr, "OR"])
                needOR = False
            expr = " ".join([expr, "("])

        if dateFrom:
            expr = "".join([expr, f"date='{dateFrom.strftime('%Y-%m-%d')}'"])
            needAND = True

        if timeFrom:
            if needAND:
                expr = " ".join([expr, "AND"])
                needAND = False
            expr = " ".join([expr, f"time>='{timeFrom.strftime('%H:%M:%S')}'"])
            needAND = True

        if dateFrom and dateTo and dateTo == dateFrom:
            if needAND:
                expr = " ".join([expr, "AND"])
                needAND = False
            expr = " ".join([expr, f"time<='{timeTo.strftime('%H:%M:%S')}'"])
            needAND = True

        if dateFrom or timeFrom:
            expr = "".join([expr, ")"])
            needOR = True
            needAND = False

        # справа
        if not dateFrom or not dateTo or dateTo != dateFrom:
            if dateTo or timeTo:
                if needOR:
                    expr = " ".join([expr, "OR"])
                    needOR = False
                expr = " ".join([expr, "("])

            if dateTo:
                expr = "".join([expr, f"date='{dateTo.strftime('%Y-%m-%d')}'"])
                needAND = True

            if timeTo:
                if needAND:
                    expr = " ".join([expr, "AND"])
                expr = " ".join([expr, f"time<='{timeTo.strftime('%H:%M:%S')}'"])

            if dateTo or timeTo:
                expr = "".join([expr, ")"])
                needOR = True
                needAND = False

        expr = " ".join([expr, ")"])

    expr = "".join([expr, ")"])

    return expr
