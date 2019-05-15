#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import text
from app.database import db
from datetime import datetime


class Results(db.Model):
    __tablename__ = "Results"
    __table_args__ = {'extend_existing': True}

    personEmail = db.Column(db.String(80), nullable=False, primary_key=True)
    model = db.Column(db.String(80), nullable=False, primary_key=True)
    preprocessor = db.Column(db.String(80), nullable=False, primary_key=True)
    resource = db.Column(db.String(80), nullable=False, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.now, server_default=text('now()'), primary_key=True)
    result = db.Column(db.String(80))

    def __repr__(self):
        return f'{type(self).__name__} <{self.personEmail}>: <{self.model}>-<{self.preprocessor}>-<{self.resource}>:' \
               f'{self.datetime}'
