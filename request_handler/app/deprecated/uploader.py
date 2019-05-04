#!/usr/bin/env python
# coding: utf-8

from flask import abort
from app.database import db
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.deprecated.datetime_handler import datetimeToFormatStr


# deprecated
def uploadRow(values: dict, data_schema: DataSchema):
    DataRow = data_schema.load(values, session=db.session, partial=True).data
    if isinstance(DataRow, dict):
        datetimeToFormatStr(DataRow)
        DataRow = data_schema.load(DataRow, session=db.session).data
    if not isinstance(DataRow, Data):
        abort(400)
    db.session.add(DataRow)
