#!/usr/bin/env python
# coding: utf-8

from flask import abort
from app.auxiliary.file_handlers.keys_normalizer import normalize_keys


def parseRow(row: list, title: dict, data_keys: list) -> dict:
    values = {}
    if len(row) != len(title):
        abort(400)
    for i in range(len(row)):
        values[title[i]] = row[i]
    normalize_keys(values, data_keys)
    return values
