#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import Flask
from appconfig import getConfig
from app.database import db

engine = create_engine(getConfig().SQLALCHEMY_DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)

app = Flask(__name__)
app.config.from_object(getConfig())

db.init_app(app)

with app.test_request_context():
    db.create_all()
