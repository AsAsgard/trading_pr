#!/usr/bin/env python
# coding: utf-8

import os
import pytest
from flask import url_for
from tests.t_data import count_lines
from app.db_entities.data_view import Data
from app.db_entities.files_view import Files


class TestPost:

    def test_empty_request_post(self, client):
        assert client.post(url_for('data_handler.upload_file')).status_code == 400

    @pytest.mark.parametrize('filepath', [
        pytest.param("request_handler/tests/csv/little_data.csv"),
        pytest.param("request_handler/tests/csv/little_data_2.csv"),
        pytest.param("request_handler/tests/csv/medium_data.csv"),
        pytest.param("request_handler/tests/csv/little_data_cp1251.csv"),
    ])
    def test_good_body_post(self, client, db_session, filepath):
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
        post_resp = client.post(url_for('data_handler.upload_file'),
                                data={'file': (filepath, os.path.basename(filepath))})
        assert post_resp.status_code == 200
        assert db_session.query(Files).all()
        assert db_session.query(Data).all()
        get_resp = client.get(url_for('data_handler.file_info', fileid=post_resp.get_json()['fileid']))
        assert get_resp.status_code == 200
        assert get_resp.is_json
        assert get_resp.get_json()['data_count'] == count_lines(filepath) - 1
        assert get_resp.get_json()['fileid'] == post_resp.get_json()['fileid']
        assert get_resp.get_json()['filename'] == os.path.basename(filepath)

    @pytest.mark.parametrize('filepath', [
        pytest.param("request_handler/tests/csv/bad_data.csv"),
        pytest.param("request_handler/tests/csv/only_title.csv"),
        pytest.param("request_handler/tests/csv/no_date_in_data.csv"),
        pytest.param("request_handler/tests/csv/no_data.csv"),
        pytest.param("request_handler/tests/csv/image.jpg"),
    ])
    def test_bad_body_post(self, client, db_session, filepath):
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
        resp = client.post(url_for('data_handler.upload_file'),
                           data={'file': (filepath, os.path.basename(filepath))})
        assert resp.status_code == 400
        assert not db_session.query(Data).all()
        assert not db_session.query(Files).all()
