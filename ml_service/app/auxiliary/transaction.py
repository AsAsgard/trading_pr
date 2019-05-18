#!/usr/bin/env python
# coding: utf-8

from contextlib import contextmanager
from functools import wraps
from app.database import db


@contextmanager
def transaction(session=db.session):
    session.begin(nested=session.is_active)
    try:
        yield
    except:
        session.rollback()
        raise
    else:
        session.commit()


def transactional(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with transaction():
            return f(*args, **kwargs)
    return wrapper
