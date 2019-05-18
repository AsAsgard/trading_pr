# main.py

import requests
import json
from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from .appconfig import nginx_url

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/profile/files/file_list')
@login_required
def data():
    response = requests.get(''.join([nginx_url, '/data/list']))
    print(json.loads(response.content))
    return render_template('file_list.html', file_list=json.loads(response.content))


@main.route('/profile/files/upload_file')
@login_required
def upload_file():
    return render_template('upload_file.html')


@main.route('/profile/files/upload_file/to', methods=['GET', 'POST'])
@login_required
def upload_file_to():
    if request.method == 'POST':
        response = requests.post(
            ''.join([nginx_url, '/data/']), files={
                'file': request.files['f'].stream.read()}, headers={'email': current_user.email,
                                                                    'filename': request.files['f'].filename})
        if response.status_code == 202:
            return render_template('upload_file.html', ans=True, err=False)
        else:
            return render_template('upload_file.html', ans=False, err=True)
    else:
        return render_template('upload_file.html')


@main.route('/profile/files/file_setup')
@login_required
def file_setup():
    return render_template('file_setup.html', ans=False)


@main.route('/profile/files/file_setup/processing', methods=['POST'])
@login_required
def file_setup_get():
    if request.method == 'POST':
        if request.form.get('select') == 'GET':
            response = requests.get(
                ''.join([nginx_url, '/data/', request.form.get('ID')]), headers={'email': current_user.email})
            return render_template('file_setup_get.html', file_list=[json.loads(response.content)])
        elif request.form.get('select') == 'PUT':
            response = requests.put(
                ''.join([nginx_url, '/data/', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('file_setup.html', ans=True)
        elif request.form.get('select') == 'PATCH':
            response = requests.patch(
                ''.join([nginx_url, '/data/', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('file_setup.html', ans=True)
        elif request.form.get('select') == 'DELETE':
            response = requests.delete(
                ''.join([nginx_url, '/data/', request.form.get('ID')]), headers={'email': current_user.email})
            if response.status_code == 204:
                return render_template('file_setup.html', ans=True)
        else:
            return 'Smth wrong'
    else:
        return render_template('upload_file.html')


@main.route('/profile/ml/run')
@login_required
def run():
    return render_template('run_input.html')


@main.route('/profile/ml/task_info')
@login_required
def task_info():
    return render_template('task_setup.html')


@main.route('/profile/ml/preproc_list')
@login_required
def preproc_list():
    response = requests.get(''.join([nginx_url, '/preprocessors/list']))
    return render_template('preproc_list.html', file_list=json.loads(response.content))


@main.route('/profile/ml/preproc_setup')
@login_required
def preproc_setup():
    return render_template('preproc_setup.html', ans=False)


@main.route('/profile/ml/preproc/processing', methods=['POST'])
@login_required
def preproc_setup_get():
    if request.method == 'POST':
        if request.form.get('select') == 'POST':
            response = requests.post(
                ''.join([nginx_url, '/preprocessors/upload']), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('preproc_setup.html', ans=True)
        elif request.form.get('select') == 'PUT':
            response = requests.put(
                ''.join([nginx_url, '/preprocessors/replace', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('preproc_setup.html', ans=True)
        elif request.form.get('select') == 'PATCH':
            response = requests.patch(
                ''.join([nginx_url, '/preprocessors/insert', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('preproc_setup.html', ans=True)
        elif request.form.get('select') == 'DELETE':
            response = requests.delete(
                ''.join([nginx_url, '/preprocessors/delete/', request.form.get('ID')]), headers={
                    'email': current_user.email})
            if response.status_code == 204:
                return render_template('preproc_setup.html', ans=True)
        else:
            return 'Smth wrong'
    else:
        return render_template('upload_file.html')


@main.route('/profile/ml/models_list')
@login_required
def models_list():
    response = requests.get(''.join([nginx_url, '/models/list']))
    return render_template('models_list.html', file_list=json.loads(response.content))


@main.route('/profile/ml/models_setup')
@login_required
def models_setup():
    return render_template('models_setup.html', ans=False)


@main.route('/profile/ml/models/processing', methods=['POST'])
@login_required
def models_setup_get():
    if request.method == 'POST':
        if request.form.get('select') == 'POST':
            response = requests.post(
                ''.join([nginx_url, '/models/upload']), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('models_setup.html', ans=True)
        elif request.form.get('select') == 'PUT':
            response = requests.put(
                ''.join([nginx_url, '/models/replace', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('models_setup.html', ans=True)
        elif request.form.get('select') == 'PATCH':
            response = requests.patch(
                ''.join([nginx_url, '/models/insert', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('models_setup.html', ans=True)
        elif request.form.get('select') == 'DELETE':
            response = requests.delete(
                ''.join([nginx_url, '/models/delete/', request.form.get('ID')]), headers={'email': current_user.email})
            if response.status_code == 204:
                return render_template('models_setup.html', ans=True)
        else:
            return 'Smth wrong'
    else:
        return render_template('upload_file.html')


@main.route('/profile/ml/resources_list')
@login_required
def resources_list():
    response = requests.get(''.join([nginx_url, '/resources/list']))
    return render_template('resources_list.html', file_list=json.loads(response.content))


@main.route('/profile/ml/resources_setup')
@login_required
def resources_setup():
    return render_template('resources_setup.html', ans=False)


@main.route('/profile/ml/resources/processing', methods=['POST'])
@login_required
def resources_setup_get():
    if request.method == 'POST':
        if request.form.get('select') == 'POST':
            response = requests.post(
                ''.join([nginx_url, '/resources/upload']), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('resources_setup.html', ans=True)
        elif request.form.get('select') == 'PUT':
            response = requests.put(
                ''.join([nginx_url, '/resources/replace', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('resources_setup.html', ans=True)
        elif request.form.get('select') == 'PATCH':
            response = requests.patch(
                ''.join([nginx_url, '/resources/insert', request.form.get('ID')]), files={
                    'file': request.files['file'].stream.read()}, headers={'email': current_user.email,
                                                                           'filename': request.files['file'].filename})
            if response.status_code == 204:
                return render_template('resources_setup.html', ans=True)
        elif request.form.get('select') == 'DELETE':
            response = requests.delete(
                ''.join([nginx_url, '/resources/delete/', request.form.get('ID')]), headers={
                    'email': current_user.email})
            if response.status_code == 204:
                return render_template('resources_setup.html', ans=True)
        else:
            return 'Smth wrong'
    else:
        return render_template('upload_file.html')


@main.route('/profile/ml/predictions_list')
@login_required
def predictions_list():
    response = requests.get(''.join([nginx_url, '/predictions/list']), headers={
                    'email': current_user.email})
    print(json.loads(response.content))
    return render_template('predictions_list.html', file_list=json.loads(response.content))


@main.route('/profile/ml/run/to', methods=['POST'])
@login_required
def run_to():
    if request.method == 'POST':
        response = requests.post(
            ''.join([nginx_url, '/predictions/run']), json={
                'model': request.form.get('model'), 'preprocessor': request.form.get('preprocessor'),
                'resource': request.form.get('resource'), 'ticker': request.form.get('tickers').upper().split(),
                'dateFrom': request.form.get('datefrom'), 'dateTo': request.form.get('dateto'),
                'timeFrom': request.form.get('timefrom'), 'timeTo': request.form.get('timeto')},
            headers={'email': current_user.email})
        if response.status_code == 202:
            return render_template('run_input.html', ans=True, err=False)
        else:
            return render_template('run_input.html', ans=False, err=True)
    else:
        return render_template('run_input.html')


@main.route('/profile/ml/predictions/task')
@login_required
def predictions_task():
    return render_template('task_setup.html', ans=False)


@main.route('/profile/ml/predictions/task', methods=['POST'])
@login_required
def predictions_task_get():
    if request.method == 'POST':
        if request.form.get('select') == 'POST':
            response = requests.get(
                ''.join([nginx_url, '/predictions/list/status/', request.form.get('ID')]), headers={
                    'email': current_user.email})
            if response.status_code == 200:
                if type(json.loads(response.content)) is dict:
                    return render_template('ml_task.html', file_list=[json.loads(response.content)])
                else:
                    return render_template('ml_task.html', file_list=json.loads(response.content))
        else:
            return 'Smth wrong'
    else:
        return render_template('upload_file.html')