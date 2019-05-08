#!/usr/bin/env python
# coding: utf-8

import pytest
import os
from flask import url_for
from app.db_entities.data_view import Data
from app.db_entities.files_view import Files
from app.schemas.data_schema import DataSchema
from tests.t_data import testData, testFilenames, count_lines


class TestPatch:

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

    @pytest.mark.parametrize('uploadedfile, filepath', [
        pytest.param("request_handler/tests/csv/little_data.csv", "request_handler/tests/csv/bad_data.csv"),
        pytest.param("request_handler/tests/csv/little_data.csv", "request_handler/tests/csv/only_title.csv"),
        pytest.param("request_handler/tests/csv/little_data.csv", "request_handler/tests/csv/no_date_in_data.csv"),
        pytest.param("request_handler/tests/csv/little_data.csv", "request_handler/tests/csv/no_data.csv"),
        pytest.param("request_handler/tests/csv/little_data.csv", "request_handler/tests/csv/image.jpg"),
    ])
    def test_bad_body_patch(self, client, db_session, uploadedfile, filepath):
        post_resp = client.post(url_for('data_handler.upload_file'),
                                data={'file': (uploadedfile, os.path.basename(uploadedfile))})
        assert post_resp.status_code == 200
        get_resp = client.get(url_for('data_handler.file_info', fileid=post_resp.get_json()['fileid']))
        assert get_resp.status_code == 200
        assert get_resp.get_json()['data_count'] == count_lines(uploadedfile) - 1
        assert get_resp.get_json()['fileid'] == post_resp.get_json()['fileid']
        assert get_resp.get_json()['filename'] == os.path.basename(uploadedfile)
        assert db_session.query(Data).all()
        assert db_session.query(Files).all()
        patch_resp = client.patch(url_for('data_handler.update_file', fileid=post_resp.get_json()['fileid']),
                                  data={'file': (filepath, os.path.basename(filepath))})
        assert patch_resp.status_code == 400
        assert db_session.query(Files).all()
        assert db_session.query(Data).all()
        get_resp = client.get(url_for('data_handler.file_info', fileid=post_resp.get_json()['fileid']))
        assert get_resp.status_code == 200
        assert get_resp.get_json()['data_count'] == count_lines(uploadedfile) - 1
        assert get_resp.get_json()['fileid'] == post_resp.get_json()['fileid']
        assert get_resp.get_json()['filename'] == os.path.basename(uploadedfile)

    @pytest.mark.parametrize('file, values_list, filepath', [
        pytest.param(Files(filename=testFilenames[0]), testData, "request_handler/tests/csv/little_data.csv"),
        pytest.param(Files(filename=testFilenames[0]), testData, "request_handler/tests/csv/little_data_2.csv"),
        pytest.param(Files(filename=testFilenames[0]), testData, "request_handler/tests/csv/medium_data.csv"),
        pytest.param(Files(filename=testFilenames[0]), testData, "request_handler/tests/csv/little_data_cp1251.csv"),
    ])
    def test_good_body_patch(self, client, db_session, file, values_list, filepath):
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
        assert db_session.query(Data).all()
        assert db_session.query(Files).all()
        patch_resp = client.patch(url_for('data_handler.update_file', fileid=file.fileid),
                                  data={'file': (filepath, os.path.basename(filepath))})
        assert patch_resp.status_code == 204
        assert db_session.query(Files).all()
        assert db_session.query(Data).all()
        get_resp = client.get(url_for('data_handler.file_info', fileid=file.fileid))
        assert get_resp.status_code == 200
        assert get_resp.get_json()['data_count'] == count_lines(filepath) - 1 + len(values_list)
        assert get_resp.get_json()['fileid'] == file.fileid
        assert get_resp.get_json()['filename'] == os.path.basename(filepath)

    @pytest.mark.parametrize('uploadedfile, filepath', [
        pytest.param("request_handler/tests/csv/2_com_2_anth.csv", "request_handler/tests/csv/little_data.csv"),
        pytest.param("request_handler/tests/csv/2_com_2_anth.csv", "request_handler/tests/csv/little_data_2.csv"),
        pytest.param("request_handler/tests/csv/2_com_2_anth.csv", "request_handler/tests/csv/medium_data.csv"),
        pytest.param("request_handler/tests/csv/2_com_2_anth.csv", "request_handler/tests/csv/little_data_cp1251.csv"),
    ])
    def test_good_intersect_patch(self, client, db_session, uploadedfile, filepath):
        post_resp = client.post(url_for('data_handler.upload_file'),
                                data={'file': (uploadedfile, os.path.basename(uploadedfile))})
        assert post_resp.status_code == 200
        get_resp = client.get(url_for('data_handler.file_info', fileid=post_resp.get_json()['fileid']))
        assert get_resp.status_code == 200
        assert get_resp.get_json()['data_count'] == count_lines(uploadedfile) - 1
        assert get_resp.get_json()['fileid'] == post_resp.get_json()['fileid']
        assert get_resp.get_json()['filename'] == os.path.basename(uploadedfile)
        assert db_session.query(Data).all()
        assert db_session.query(Files).all()
        patch_resp = client.patch(url_for('data_handler.update_file', fileid=post_resp.get_json()['fileid']),
                                  data={'file': (filepath, os.path.basename(filepath))})
        assert patch_resp.status_code == 204
        assert db_session.query(Files).all()
        assert db_session.query(Data).all()
        get_resp = client.get(url_for('data_handler.file_info', fileid=post_resp.get_json()['fileid']))
        assert get_resp.status_code == 200
        assert get_resp.get_json()['data_count'] == count_lines(filepath) - 1 + 2
        assert get_resp.get_json()['fileid'] == post_resp.get_json()['fileid']
        assert get_resp.get_json()['filename'] == os.path.basename(filepath)
