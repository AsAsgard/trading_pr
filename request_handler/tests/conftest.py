#!/usr/bin/env python
# coding: utf-8

import pytest
from app import create_app
from app.database import db
from appconfig import currentConfig


@pytest.yield_fixture(scope="session")
def app():
    app = create_app()
    app.debug = True
    app.config['TESTING'] = True
    yield app


@pytest.yield_fixture(scope="session")
def _db(app):
    return db
