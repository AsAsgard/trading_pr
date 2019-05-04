#!/usr/bin/env python
# coding: utf-8

import re


def normalize_keys(titles: list):

    def norm_key(key):
        reg = re.compile('[^a-zA-Z]')
        return reg.sub('', key).lower()

    return [norm_key(key) for key in titles]
