#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.transaction import transactional
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.file_handlers.parser import parseRow
from app.auxiliary.file_handlers.uploader import uploadRow
from flask import abort
from werkzeug.datastructures import FileStorage
import csv


@transactional
def handleFile(fileid: int, file: FileStorage):
    with open(file=file.read(), mode="r") as f:
        reader = csv.reader(f)
        if not reader:
            abort(400)
        # Считываем первую строку
        title = None
        try:
            title = next(reader)
        except StopIteration:
            abort(400)
        if not title:
            abort(400)
        # Считываем данные
        values = None
        data_schema = DataSchema()
        data_keys = data_schema.dump(Data()).data.keys()
        for row in reader:
            values = parseRow(row, title, data_keys)
            values['fileid'] = fileid
            uploadRow(values, data_schema)
        if not values:
            abort(400)
