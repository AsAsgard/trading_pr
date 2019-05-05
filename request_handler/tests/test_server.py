#!/usr/bin/env python
# coding: utf-8

import pytest
from flask import url_for
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data


class TestServer:
    def test_server(self, client, db_session):
        assert client.get(url_for('data_handler.file_info', fileid=248)).status_code == 404
        db_session.query(Data).delete()
        db_session.query(Files).delete()
        db_session.commit()
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()

    def test_second(self, db_session):
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
