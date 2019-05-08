#!/usr/bin/env python
# coding: utf-8

import pytest
from flask import url_for
from app.db_entities.data_view import Data
from app.db_entities.files_view import Files
from app.schemas.data_schema import DataSchema
from tests.t_data import testData, testFilenames


class TestPatchPut:

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_empty_request_patch(self, client, db_session, file, values_list):
        db_session.add(file)
        db_session.commit()
        assert db_session.query(Files).all() == [file]
        samples = []
        data_schema = DataSchema()
        for values in values_list:
            values['fileid'] = file.fileid
            sample = data_schema.load(values, session=db_session, partial=True).data
            assert isinstance(sample, Data)
            samples.append(sample)
            db_session.add(sample)
        db_session.commit()
        assert db_session.query(Data).all() == samples
        assert client.patch(url_for('data_handler.update_file', fileid=file.fileid)).status_code == 400
        assert client.patch(url_for('data_handler.update_file', fileid=file.fileid + 1)).status_code == 404
        assert db_session.query(Files).all() == [file]
        assert db_session.query(Data).all() == samples

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_empty_request_put(self, client, db_session, file, values_list):
        db_session.add(file)
        db_session.commit()
        assert db_session.query(Files).all() == [file]
        samples = []
        data_schema = DataSchema()
        for values in values_list:
            values['fileid'] = file.fileid
            sample = data_schema.load(values, session=db_session, partial=True).data
            assert isinstance(sample, Data)
            samples.append(sample)
            db_session.add(sample)
        db_session.commit()
        assert db_session.query(Data).all() == samples
        assert client.put(url_for('data_handler.change_file', fileid=file.fileid)).status_code == 400
        assert client.put(url_for('data_handler.change_file', fileid=file.fileid + 1)).status_code == 404
        assert db_session.query(Files).all() == [file]
        assert db_session.query(Data).all() == samples

    @pytest.mark.parametrize('filepath', [
        pytest.param("request_handler/tests/csv/bad_data.csv"),
        pytest.param("request_handler/tests/csv/only_title.csv"),
        pytest.param("request_handler/tests/csv/no_date_in_data.csv"),
        pytest.param("request_handler/tests/csv/no_data.csv"),
        pytest.param("request_handler/tests/csv/image.jpg"),
    ])
    def test_bad_body(self, client, db_session, filepath):
        pass
