#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import text
from app.database import db
from datetime import datetime


class Data(db.Model):
    __tablename__ = "Data"
    __table_args__ = {'extend_existing': True}

    fileid = db.Column(db.Integer, db.ForeignKey('Files.fileid'))
    ticker = db.Column(db.String(80), nullable=False, primary_key=True)
    per = db.Column(db.Integer())
    date = db.Column(db.Date, nullable=False, primary_key=True)
    time = db.Column(db.Time, nullable=False, primary_key=True)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    vol = db.Column(db.Integer)

    created = db.Column(db.DateTime, default=datetime.now, server_default=text('now()'))
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, server_default=text('now()'))

    def __repr__(self):
        return f'{type(self).__name__} <{self.fileid}>=<{self.nodeid}>'
