#!/usr/bin/env python
# coding: utf-8

from appconfig import upload_folder
from flask import Blueprint
from app.auxiliary import storage_functions

models_handler = Blueprint('models_handler', __name__, url_prefix="/models")
model_parameters = {
    'folder': upload_folder + '/models/',
    'extension': '.py',
    'entity': 'model',
}


# Загрузка модели
@models_handler.route('/upload', methods=['POST'])
def model_upload():
    return storage_functions.storage_upload(model_parameters)


# Замена модели
@models_handler.route('/replace', methods=['PUT'])
def model_replace():
    return storage_functions.storage_replace(model_parameters)


# Загрузка или изменение модели
@models_handler.route('/insert', methods=['PATCH'])
def model_insert():
    return storage_functions.storage_insert(model_parameters)


# Список загруженных моделей
@models_handler.route('/list', methods=['GET'])
def model_list():
    return storage_functions.storage_list(model_parameters)


# Удаление модели
@models_handler.route('/delete/<filename>', methods=['DELETE'])
def model_delete(filename):
    return storage_functions.storage_delete(model_parameters, filename)
