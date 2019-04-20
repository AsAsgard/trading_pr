#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import text
from app.database import db
from datetime import datetime


class Files(db.Model):
    __tablename__ = "Files"
    __table_args__ = {'extend_existing': True}

    fileid = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)

    data = db.relationship("Data", backref='Files', lazy="dynamic")

    first_download = db.Column(db.DateTime, default=datetime.now, server_default=text('now()'))
    last_download = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, server_default=text('now()'))

    def __repr__(self):
        return f'{type(self).__name__} <{self.fileid}>=<{self.filename}>'
