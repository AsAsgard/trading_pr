#!/usr/bin/env python
# coding: utf-8

import logging.config


# Конфигурация базы данных
DB_CONFIG = {
    'username': 'root',
    'password': 'trading_pass',
    'host': '127.0.0.1',
    'dbname': 'trading_db',
}


# Конфигурация журналирования
LOGGING = {
    'version': 1,
    'formatters': {  # Форматирование сообщения
        'main': {
            'format': '[%(asctime)s] %(levelname)s %(module)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },

    'handlers': {  # Обработчикаи сообщений
        'file_handler': {
            'class': 'logging.FileHandler',
            'filename': '/tmp/trading.log',
            'formatter': 'main',
        },
        'streamlogger': {
            'class': 'logging.StreamHandler',
            'formatter': 'main',
        },
    },

    'loggers': {   # Логгеры
        'prod_logger': {
            'handlers': ['file_handler', 'streamlogger'],
            'level': 'INFO',
        },
        'devel_logger': {
            'handlers': ['file_handler', 'streamlogger'],
            'level': 'DEBUG',
        },
    },
}

logging.config.dictConfig(LOGGING)


# Базовая конфигурация
class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}" \
                              f"@{DB_CONFIG['host']}/{DB_CONFIG['dbname']}?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGGER_NAME = 'devel_logger'


# Конфигурация выпуска
class ProductionConfig(Config):
    DEBUG = False
    LOGGER_NAME = 'prod_logger'


# Конфигурация разработки
class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    LOGGER_NAME = 'devel_logger'


# Конфигурация тестирования
class TestConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOGGER_NAME = 'devel_logger'
    test_db_name = "test_trading_db"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}" \
                              f"@{DB_CONFIG['host']}/{test_db_name}?charset=utf8"

# Текущая конфигурация
# --------------------------------------------------
_currentConfig = DevelopmentConfig


def getConfig():
    return _currentConfig


def setConfig(config):
    global _currentConfig
    _currentConfig = config
# --------------------------------------------------

# Размер буффера данных, загружаемых в базу
chunkSize = 30000
