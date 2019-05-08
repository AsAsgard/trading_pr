#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from appconfig import getConfig
from app.database import db
from app import create_app


def migrate(app):
    engine = create_engine(getConfig().SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)
    assert database_exists(engine.url)

    with app.test_request_context():
        db.create_all()


if __name__ == "__main__":
    app = create_app()
    migrate(app)
