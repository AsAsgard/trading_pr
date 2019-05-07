#!/usr/bin/env python
# coding: utf-8

import os
import pytest
from flask import url_for


class TestPost:

    def test_empty_request_post(self, client):
        assert client.post(url_for('data_handler.upload_file')).status_code == 400

    @pytest.mark.parametrize('filepath', [pytest.param("request_handler/tests/csv/sber_170101_181235.csv")])
    def test_good_body_post(self, client, db_session, filepath):
        with open(filepath, 'r') as f:
            resp = client.post(url_for('data_handler.upload_file'),
                               data={'file': (filepath, os.path.basename(filepath))})
            print(resp.data)
            assert resp.status_code == 200
