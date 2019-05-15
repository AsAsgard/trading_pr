# main.py

import requests
from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/profile/file_list')
@login_required
def data():
    response = requests.get('http://0.0.0.0:8087/data/list')
    return render_template('file_list.html', file_list=response.content)


@main.route('/profile/upload_file')
@login_required
def upload_file():
    return render_template('upload_file.html')


@main.route('/profile/upload_file/to', methods=['GET', 'POST'])
@login_required
def upload_file_to():
    if request.method == 'POST':
        print(request.files)
        response = requests.post('http://0.0.0.0:8087/data/', data={'file': request.files['f']}, headers={'user_email': current_user.email})
        return response.content
    else:
        return render_template('upload_file.html')
