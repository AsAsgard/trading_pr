#!/usr/bin/env python
# coding: utf-8

import pytest
from flask import url_for
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from sqlalchemy.exc import OperationalError

testFilenames = ['some_file', 'one_more_file', 'third_file']

testData = [
    {
        'ticker': "TEST_TICKER",
        'per': 1,
        'date': "2019-05-08",
        'time': "10:08:15",
        'open': 174.15,
        'close': 174.65,
        'high': 175.15,
        'low': 172.15,
        'vol': 43223
    },
    {
        'ticker': "TEST_TICKER",
        'per': 1,
        'date': "2019-05-08",
        'time': "10:08:16",
        'open': 173.15,
        'close': 173.65,
        'high': 174.15,
        'low': 171.15,
        'vol': 122423
    },
    {
        'ticker': "TEST_TICKER",
        'per': 1,
        'date': "2019-05-08",
        'time': "10:08:17",
        'open': 174.85,
        'close': 175.65,
        'high': 176.15,
        'low': 173.15,
        'vol': 32223
    },
]


class TestServer:
    def test_creation(self, db_session):
        try:
            assert not db_session.query(Files).all()
            assert not db_session.query(Data).all()
        except OperationalError:
            assert False
        else:
            assert True

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_transactional_add_delete(self, db_session, file, values_list):
        db_session.add(file)
        db_session.commit()
        assert db_session.query(Files).all() == [file]
        samples = []
        data_schema = DataSchema()
        for values in values_list:
            values['fileid'] = file.fileid
            sample = data_schema.load(values, session=db_session, partial=True).data
            assert isinstance(sample, Data)
            db_session.add(sample)
            samples.append(sample)
        db_session.commit()
        assert db_session.query(Data).all() == samples
        db_session.query(Data).delete()
        db_session.query(Files).delete()
        db_session.commit()
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()

    @pytest.mark.parametrize('file, values_list', [pytest.param(Files(filename=fn), testData) for fn in testFilenames])
    def test_transactional_add(self, db_session, file, values_list):
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

    def test_nothing_changed(self, db_session):
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()

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
