#!/usr/bin/env python
# coding: utf-8

from flask import abort
from app.database import db
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from app.auxiliary.file_handlers.datetime_handler import datetimeToFormatStr
from sqlalchemy.dialects.mysql import insert
from appconfig import chunkSize


# deprecated
def uploadRow(values: dict, data_schema: DataSchema):
    DataRow = data_schema.load(values, session=db.session, partial=True).data
    if isinstance(DataRow, dict):
        datetimeToFormatStr(DataRow)
        DataRow = data_schema.load(DataRow, session=db.session).data
    if not isinstance(DataRow, Data):
        abort(400)
    db.session.add(DataRow)


def uploadToDB(df):

    def insertChunk(inserterStatemant):
        if last_boarder == 0:
            for key in data_keys.keys():
                if key in dicts[0].keys() or key=='updated':
                    try:
                        norm_data_keys[key] = getattr(inserterStatemant.inserted, key)
                    except AttributeError:
                        pass
        inserterStatemant = inserterStatemant.on_duplicate_key_update(
            fileid=inserterStatemant.inserted.fileid,
            ticker=inserterStatemant.inserted.ticker,
            per=inserterStatemant.inserted.per,
            date=inserterStatemant.inserted.date,
            time=inserterStatemant.inserted.time,
            open=inserterStatemant.inserted.open,
            close=inserterStatemant.inserted.close,
            high=inserterStatemant.inserted.high,
            low=inserterStatemant.inserted.low,
            vol=inserterStatemant.inserted.vol,
            updated=inserterStatemant.inserted.updated,
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
