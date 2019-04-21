#!/usr/bin/env python
# coding: utf-8

from flask import abort
from app.database import db
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema


def uploadRow(values: dict, data_schema: DataSchema):
    DataRow = data_schema.load(values, session=db.session).data
    print(f"Values: {values}")
    print(f"DataRow: {DataRow}")
    if not isinstance(DataRow, Data):
        abort(400)
    db.query.add(DataRow)
