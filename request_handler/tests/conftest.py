#!/usr/bin/env python
# coding: utf-8

import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database
from app import create_app
from app.database import db
from appconfig import setConfig, getConfig, TestConfig


@pytest.yield_fixture(scope="session")
def app():
    setConfig(TestConfig)
    app = create_app()
    yield app


@pytest.yield_fixture(scope="session")
def _db(app):
    dsn = getConfig().SQLALCHEMY_DATABASE_URI
    assert not database_exists(dsn)
    create_database(dsn)
    assert database_exists(dsn)
    with app.test_request_context():
        db.create_all()
    yield db
    db.session.remove()
    drop_database(dsn)
    assert not database_exists(dsn)
