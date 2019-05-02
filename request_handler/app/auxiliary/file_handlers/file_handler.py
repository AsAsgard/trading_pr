#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.transaction import transactional
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.file_handlers.parser import parseRow
from app.auxiliary.file_handlers.uploader import uploadRow
from flask import abort
from werkzeug.datastructures import FileStorage
from pandas import read_csv, errors
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
    index, title = next(df.iterrows())
    title = title.tolist()

    # НЕОБХОДИМО ОТПРОФИЛИРОВАТЬ И ОПТИМИЗИРОВАТЬ!-------------
    # Считываем данные
    values = None
    data_schema = DataSchema()
    data_keys = data_schema.dump(Data()).data.keys()
    str = StringIO(file.stream.readline().decode("utf-8"))
    while str:
        try:
            df = read_csv(str, sep='[;,|]', engine="python", names=title)
        except errors.ParserError:
            abort(400)
        if df.empty:
            break
        values = parseRow(df, data_keys)
        values['fileid'] = fileid
        uploadRow(values, data_schema)
        str = StringIO(file.stream.readline().decode("utf-8"))
    # ---------------------------------------------------------
    if not values:
        abort(400)
