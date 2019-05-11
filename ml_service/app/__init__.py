#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from app.database import db
import appconfig
from app.logger import Logger


def create_app():

    Logger.info('Creating app...')
    app = Flask(__name__)
    Logger.info('App created')
    Logger.info('Configurating config...')
    app.config.from_object(appconfig.getConfig())
    Logger.info('Config configured')

    Logger.info('Initialize database...')
    db.init_app(app)
    Logger.info('Database initialized')

    import app.queries.upload_handler as upload_handler
    import app.queries.ml_handler as ml_handler

    app.register_blueprint(upload_handler.upload_handler)
    app.register_blueprint(ml_handler.ml_handler)

    return app
