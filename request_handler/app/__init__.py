#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from app.database import db
import appconfig
from app.logger import Logger
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data


def create_app():

    Logger.info('Creating app...')
    app = Flask(__name__)
    Logger.info('App created')
    Logger.info('Configure app...')
    app.config.from_object(appconfig.getConfig())
    Logger.info('App configured')

    Logger.info('Initialize database...')
    db.init_app(app)
    Logger.info('Database initialized')

    import app.queries.data_handler as data_handler

    app.register_blueprint(data_handler.data_handler)

    return app
