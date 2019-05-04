#!/usr/bin/env python
# coding: utf-8

from app.database import db
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from sqlalchemy.dialects.mysql import insert
from appconfig import chunkSize


def uploadToDB(df):

    def insertChunk(inserterStatemant):
        for key in data_keys.keys():
            if key in dicts[0].keys() or key=='updated':
                try:
                    norm_data_keys[key] = getattr(inserterStatemant.inserted, key)
                except AttributeError:
                    pass
        inserterStatemant = inserterStatemant.on_duplicate_key_update(
            norm_data_keys
        )
        db.session.execute(inserterStatemant)

    dicts = df.to_dict('records')
    data_schema = DataSchema()
    data_keys = data_schema.dump(Data()).data
    norm_data_keys = {}
    last_boarder = 0
    for i in range(chunkSize, len(dicts), chunkSize):
        inserterStatemant = insert(Data.__table__).values(
            dicts[i - chunkSize:i]
        )
        insertChunk(inserterStatemant)
        last_boarder = i
    if last_boarder != len(dicts):
        inserterStatemant = insert(Data.__table__).values(
            dicts[last_boarder:len(dicts)]
        )
        insertChunk(inserterStatemant)
