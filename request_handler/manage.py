#!/usr/bin/env python
# coding: utf-8

from flask_script import Manager
from app.logger import Logger
from app import create_app

app = create_app()
manager = Manager(app)


if __name__ == "__main__":
    Logger.info('Starting server')
    manager.run()
