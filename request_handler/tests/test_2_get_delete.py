#!/usr/bin/env python
# coding: utf-8

import pytest
from flask import url_for
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from tests.t_data import testFilenames, testData


class TestGetDelete:

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_get(self, client, db_session, file, values_list):
        assert client.get(url_for('data_handler.file_info', fileid=1)).status_code == 404
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
        resp = client.get(url_for('data_handler.file_info', fileid=file.fileid))
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.get_json()['data_count'] == len(values_list)
        assert resp.get_json()['fileid'] == file.fileid
        assert resp.get_json()['filename'] == file.filename

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_delete(self, client, db_session, file, values_list):
        assert client.get(url_for('data_handler.file_info', fileid=1)).status_code == 404
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
        resp = client.get(url_for('data_handler.file_info', fileid=file.fileid))
        assert resp.status_code == 200
        assert client.delete(url_for('data_handler.delete_file', fileid=file.fileid + 1)).status_code == 404
        deleter = client.delete(url_for('data_handler.delete_file', fileid=file.fileid))
        assert deleter.status_code == 204
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
        assert client.get(url_for('data_handler.file_info', fileid=file.fileid)).status_code == 404

    @pytest.mark.parametrize('files_list, values_list', [
        pytest.param([Files(filename=fn) for fn in testFilenames], testData),
    ])
    def test_multi_get_delete(self, client, db_session, files_list, values_list):
        test_len = min(len(files_list), len(values_list))
        data_schema = DataSchema()
        samples = []
        for i in range(test_len):
            db_session.add(files_list[i])
            db_session.commit()
            values_list[i]['fileid'] = files_list[i].fileid
            sample = data_schema.load(values_list[i], session=db_session, partial=True).data
            assert isinstance(sample, Data)
            db_session.add(sample)
            samples.append(sample)
            db_session.commit()
        assert db_session.query(Data).all() == samples
        for i in range(test_len):
            resp = client.get(url_for('data_handler.file_info', fileid=files_list[i].fileid))
            assert resp.status_code == 200
            assert resp.is_json
            assert resp.get_json()['data_count'] == 1
            assert resp.get_json()['fileid'] == files_list[i].fileid
            assert resp.get_json()['filename'] == files_list[i].filename
        for i in range(test_len):
            deleter = client.delete(url_for('data_handler.delete_file', fileid=files_list[0].fileid))
            assert deleter.status_code == 204
            assert client.get(url_for('data_handler.file_info', fileid=files_list[0].fileid)).status_code == 404
            if i != test_len - 1:
                assert client.get(url_for('data_handler.file_info', fileid=files_list[1].fileid)).status_code == 200
            samples.pop(0)
            files_list.pop(0)
            assert db_session.query(Data).all() == samples
            assert db_session.query(Files).all() == files_list
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
