#!/usr/bin/env python
# coding: utf-8

import pytest
from sqlalchemy_utils import database_exists, drop_database
from app import create_app
from app.database import db
from migrate import migrate
from appconfig import setConfig, getConfig, TestConfig

test_counter = 0

@pytest.yield_fixture(scope="session")
def app():
    setConfig(TestConfig)
    app = create_app()
    yield app


@pytest.yield_fixture(scope="session")
def _db(app):
    dsn = getConfig().SQLALCHEMY_DATABASE_URI
    assert not database_exists(dsn)
    migrate(app)
    yield db
    db.session.remove()
    drop_database(dsn)
    assert not database_exists(dsn)

@pytest.fixture()
def test_num():
    global test_counter
    test_counter += 1
    return test_counter
