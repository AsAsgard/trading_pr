#!/usr/bin/env python
# coding: utf-8

import pytest
from flask import url_for
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from sqlalchemy.exc import OperationalError

testFilenames = ['some_file', 'one_more_file']

testData = [
    {
        'ticker': "TEST_TICKER",
        'per': 1,
        'date': "2019-05-08",
        'time': "10-08-15",
        'open': 174.15,
        'close': 174.65,
        'high': 175.15,
        'low': 172.15,
        'vol': 43223
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

    @pytest.mark.parametrize('file', [Files(filename=fn) for fn in testFilenames])
    @pytest.mark.parametrize('values', [dataSample for dataSample in testData])
    def test_transactional_add_delete(self, db_session, file, values):
        #assert client.get(url_for('data_handler.file_info', fileid=248)).status_code == 404
        db_session.add(file)
        db_session.commit()
        assert db_session.query(Files).all() == [file]
        db_session.commit()
        data_schema = DataSchema()
        values['fileid'] = file.fileid
        sample = data_schema.load(values, session=db_session, partial=True).data
        assert isinstance(sample, Data)
        db_session.add(sample)
        assert db_session.query(Data).all() == [sample]
        db_session.query(Data).delete()
        db_session.query(Files).delete()
        db_session.commit()
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()

    @pytest.mark.parametrize('file', [Files(filename=fn) for fn in testFilenames])
    @pytest.mark.parametrize('values', [dataSample for dataSample in testData])
    def test_transactional_add(self, db_session, file, values):
        db_session.add(file)
        db_session.commit()
        assert db_session.query(Files).all() == [file]
        data_schema = DataSchema()
        values['fileid'] = file.fileid
        sample = data_schema.load(values, session=db_session, partial=True).data
        assert isinstance(sample, Data)
        db_session.add(sample)
        db_session.commit()
        assert db_session.query(Data).all() == [sample]

    def test_nothing_changed(self, db_session):
        assert not db_session.query(Files).all()
        assert not db_session.query(Data).all()
