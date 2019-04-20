#!/usr/bin/env python
# coding: utf-8

from marshmallow_sqlalchemy import ModelSchema
from app.db_entities.data_view import Data
from app.database import db


class DataSchema(ModelSchema):
    class Meta:
        model = Data
        sqla_session = db.session
