#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from appconfig import getConfig
from app.logger import Logger
from app.database import db
from app import create_app


def migrate(app):
    engine = create_engine(getConfig().SQLALCHEMY_DATABASE_URI)

    Logger.info('Check database existence...')
    if not database_exists(engine.url):
        Logger.info('Creating database...')
        create_database(engine.url)
        Logger.info('Database created')
    else:
        Logger.info('Database already exists. Not need to create')
    assert database_exists(engine.url)
    Logger.info('Database exists')

    Logger.info('Creating tables...')
    with app.test_request_context():
        db.create_all()
    Logger.info('Tables created')


if __name__ == "__main__":
    app = create_app()
    migrate(app)
