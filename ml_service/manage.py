#!/usr/bin/env python
# coding: utf-8

from flask_script import Manager
from app.logger import Logger
from fl_app import application

manager = Manager(application)


if __name__ == "__main__":
    Logger.info('Starting server')
    manager.run()
