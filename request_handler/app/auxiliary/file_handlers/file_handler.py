#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.transaction import transactional
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.file_handlers.keys_normalizer import normalize_keys
from app.auxiliary.file_handlers.parser import parseRow
from app.auxiliary.file_handlers.uploader import uploadRow
from flask import abort
from werkzeug.datastructures import FileStorage
from pandas import read_csv, read_table, errors
from io import StringIO


@transactional
def handleFile(fileid: int, file: FileStorage):
    str = StringIO(file.stream.readline().decode("utf-8"))
    if not str:
        abort(400)

    df = None
    try:
        df = read_csv(str, sep='[;,|]', engine="python", header=None)
    except errors.ParserError:
        abort(400)

    if df.empty:
        abort(400)
    index, titles = next(df.iterrows())
    titles = titles.tolist()
    titles = normalize_keys(titles)

    # НЕОБХОДИМО ОТПРОФИЛИРОВАТЬ И ОПТИМИЗИРОВАТЬ!-------------
    # Считываем данные
    filedata = file.stream.read().decode('utf-8').replace(';',',').replace('|',',')
    try:
        df = read_csv(StringIO(filedata), sep=',', names=titles)
    except errors.ParserError:
        abort(400)
    if df.empty:
        abort(400)
    print(df)
    # ---------------------------------------------------------
