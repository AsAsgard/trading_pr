#!/usr/bin/env python
# coding: utf-8

from flask import abort
from app.auxiliary.file_handlers.keys_normalizer import normalize_keys


def parseRow(df, data_keys: list) -> dict:
    values = df.to_dict(orient='list')
    for key, value_list in values.items():
        values[key] = value_list[0]
    normalize_keys(values, data_keys)
    return values
