#!/usr/bin/env python
# coding: utf-8

from manage import app
from flask import Blueprint
from app.auxiliary import storage_functions

resources_handler = Blueprint('resources_handler', __name__, url_prefix="/resources")
res_parameters = {
    'folder': app.config['UPLOAD_FOLDER'] + '/resources/',
    'extension': '.pkl',
    'entity': 'resource',
}


# Загрузка ресурса
@resources_handler.route('/upload', methods=['POST'])
def resource_upload():
    return storage_functions.storage_upload(res_parameters)


# Замена ресурса
@resources_handler.route('/replace', methods=['PUT'])
def resource_replace():
    return storage_functions.storage_replace(res_parameters)


# Загрузка или изменение ресурса
@resources_handler.route('/insert', methods=['PATCH'])
def resource_insert():
    return storage_functions.storage_insert(res_parameters)


# Список загруежнных ресурсов
@resources_handler.route('/list', methods=['GET'])
def resource_list():
    return storage_functions.storage_list(res_parameters)


# Удаление ресурса
@resources_handler.route('/delete/<filename>', methods=['DELETE'])
def resource_delete(filename):
    return storage_functions.storage_delete(res_parameters, filename)
