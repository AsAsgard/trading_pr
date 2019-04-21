#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.file_handlers.keys_normalizer import normalize_keys
from dateutil.parser import parse
from datetime import datetime


DateTime_fields = {
    'date': 'date',
    'time': 'time',
    'datetime': None,
}


def parseRow(df, data_keys: list) -> dict:
    values = df.to_dict(orient='list')
    for key, value_list in values.items():
        values[key] = value_list[0]
    normalize_keys(values, data_keys)

    # Обработка даты и времени
    if DateTime_fields.get('date') in values.keys():
        values[DateTime_fields.get('date')] = parse(str(values[DateTime_fields.get('date')])).date()
    if DateTime_fields.get('time') in values.keys():
        values[DateTime_fields.get('time')] = parse(str(values[DateTime_fields.get('time')])).time()
    if DateTime_fields.get('datetime') in values.keys():
        values[DateTime_fields.get('datetime')] = datetime.combine(values[DateTime_fields.get('date')],
                                                                   values[DateTime_fields.get('time')])

    return values
