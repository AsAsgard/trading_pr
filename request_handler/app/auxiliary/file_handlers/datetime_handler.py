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


def parseStrDateTime(df):
    try:
        if DateTime_fields.get('date') in df.keys():
            df[DateTime_fields.get('date')] = df[DateTime_fields.get('date')].map(
                lambda daterow: parse(str(daterow)).date().strftime("%Y-%m-%d")
            )
        if DateTime_fields.get('time') in df.keys():
            df[DateTime_fields.get('time')] = df[DateTime_fields.get('time')].map(
                lambda timerow: parse(" ".join(("19700101", str(timerow)))).time().strftime("%H:%M:%S")
            )
        '''
        if DateTime_fields.get('datetime') in df.keys() and \
           DateTime_fields.get('date') in df.keys() and \
           DateTime_fields.get('time') in df.keys():
            df[DateTime_fields.get('datetime')] = df[DateTime_fields.get('datetime')].map(
                lambda datetimerow: datetime.combine(df[DateTime_fields.get('date')], df[DateTime_fields.get('time')])
            )
        '''
    except ValueError:
        abort(400)


# deprecated
def datetimeToFormatStr(df):
    if DateTime_fields.get('date') in df.keys() and isinstance(df[DateTime_fields.get('date')], date):
        df[DateTime_fields.get('date')] = df[DateTime_fields.get('date')].strftime("%Y-%m-%d")
    if DateTime_fields.get('time') in df.keys() and isinstance(df[DateTime_fields.get('time')], time):
        df[DateTime_fields.get('time')] = df[DateTime_fields.get('time')].strftime("%H:%M:%S")
    if DateTime_fields.get('datetime') in df.keys() and isinstance(df[DateTime_fields.get('datetime')], datetime):
        df[DateTime_fields.get('datetime')] = df[DateTime_fields.get('datetime')].strftime("%Y-%m-%d %H:%M:%S")
