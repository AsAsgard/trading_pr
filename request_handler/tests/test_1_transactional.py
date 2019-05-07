#!/usr/bin/env python
# coding: utf-8

import pytest
from app.db_entities.files_view import Files
from app.db_entities.data_view import Data
from app.schemas.data_schema import DataSchema
from sqlalchemy.exc import OperationalError
from tests.t_data import testFilenames, testData


class TestTransactional:

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
