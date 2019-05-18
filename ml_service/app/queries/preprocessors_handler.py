#!/usr/bin/env python
# coding: utf-8

from appconfig import upload_folder
from flask import Blueprint
from app.auxiliary import storage_functions

preprocessors_handler = Blueprint('preprocessors_handler', __name__, url_prefix="/preprocessors")
prep_parameters = {
    'folder': upload_folder + '/preprocessors/',
    'extension': '.py',
    'entity': 'preprocessor',
}


# Загрузка препроцессора
@preprocessors_handler.route('/upload', methods=['POST'])
def preprocessor_upload():
    return storage_functions.storage_upload(prep_parameters)


# Замена препроцессора
@preprocessors_handler.route('/replace', methods=['PUT'])
def preprocessor_replace():
    return storage_functions.storage_replace(prep_parameters)


# Загрузка или изменение препроцессора
@preprocessors_handler.route('/insert', methods=['PATCH'])
def preprocessor_insert():
    return storage_functions.storage_insert(prep_parameters)


# Список загруженных препроцессоров
@preprocessors_handler.route('/list', methods=['GET'])
def prepocessor_list():
    return storage_functions.storage_list(prep_parameters)


# Удаление препроцессора
@preprocessors_handler.route('/delete/<filename>', methods=['DELETE'])
def prepocessor_delete(filename):
    return storage_functions.storage_delete(prep_parameters, filename)
