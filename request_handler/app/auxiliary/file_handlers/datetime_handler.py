#!/usr/bin/env python
# coding: utf-8

from datetime import datetime, date, time
from dateutil.parser import parse
from flask import abort

DateTime_fields = {
    'date': 'date',
    'time': 'time',
    'datetime': None,
}


def parseStrDateTime(val):
    try:
        if DateTime_fields.get('date') in val.keys():
            val[DateTime_fields.get('date')] = parse(str(val[DateTime_fields.get('date')])).date()
        if DateTime_fields.get('time') in val.keys():
            val[DateTime_fields.get('time')] = parse(" ".join(("19700101", str(val[DateTime_fields.get('time')])))).time()
        if DateTime_fields.get('datetime') in val.keys():
            val[DateTime_fields.get('datetime')] = datetime.combine(val[DateTime_fields.get('date')],
                                                                       val[DateTime_fields.get('time')])
    except ValueError:
        abort(400)


def datetimeToFormatStr(val):
    if DateTime_fields.get('date') in val.keys() and isinstance(val[DateTime_fields.get('date')], date):
        val[DateTime_fields.get('date')] = val[DateTime_fields.get('date')].strftime("%Y-%m-%d")
    if DateTime_fields.get('time') in val.keys() and isinstance(val[DateTime_fields.get('time')], time):
        val[DateTime_fields.get('time')] = val[DateTime_fields.get('time')].strftime("%H:%M:%S")
    if DateTime_fields.get('datetime') in val.keys() and isinstance(val[DateTime_fields.get('datetime')], datetime):
        val[DateTime_fields.get('datetime')] = val[DateTime_fields.get('datetime')].strftime("%Y-%m-%d %H:%M:%S")
