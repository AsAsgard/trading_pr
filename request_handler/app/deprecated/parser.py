#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.file_handlers.keys_normalizer import normalize_keys
from app.deprecated.datetime_handler import datetimeToFormatStr, parseStrDateTime


# deprecated
def parseRow(df) -> dict:
    values = df.to_dict(orient='list')
    for key, value_list in values.items():
        values[key] = value_list[0]
    normalize_keys(values)

    # Обработка даты и времени
    parseStrDateTime(values)
    datetimeToFormatStr(values)

    return values
