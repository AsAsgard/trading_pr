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

    import app.queries.preprocessors_handler as preprocessors_handler
    import app.queries.resources_handler as resources_handler
    import app.queries.models_handler as models_handler
    import app.queries.ml_handler as ml_handler

    app.register_blueprint(preprocessors_handler.preprocessors_handler)
    app.register_blueprint(resources_handler.resources_handler)
    app.register_blueprint(models_handler.models_handler)
    app.register_blueprint(ml_handler.ml_handler)

    return app
