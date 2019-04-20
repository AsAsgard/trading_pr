#!/usr/bin/env python
# coding: utf-8

from app.auxiliary.transaction import transactional
from app.database import db
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.keys_normalizer import normalize_keys
from flask import abort
import csv


@transactional
def parseAndUploadData(fileid: int, file):
    with open(file=file, mode="r") as f:
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
        values = {}
        data_schema = DataSchema()
        data_keys = data_schema.dump(Data()).data.keys()
        for row in reader:
            if len(row) != len(title):
                abort(400)
            for i in range(len(row)):
                values[title[i]] = row[i]
            values['fileid'] = fileid
            normalize_keys(values, data_keys)
            DataRow = data_schema.load(values, session=db.session).data
            if not isinstance(DataRow, Data):
                abort(400)
            db.query.add(DataRow)
        if not values:
            abort(400)
