#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import Flask
from appconfig import currentConfig
from app.database import db
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data

engine = create_engine(currentConfig.SQLALCHEMY_DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)

app = Flask(__name__)
app.config.from_object(currentConfig)

db.init_app(app)

with app.test_request_context():
    db.create_all()
