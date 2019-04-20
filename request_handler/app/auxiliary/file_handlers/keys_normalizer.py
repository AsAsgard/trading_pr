#!/usr/bin/env python
# coding: utf-8

import re
from copy import deepcopy


def normalize_keys(input: dict, expected: list):
    keys = deepcopy(input.keys())
    for key in keys:
        for exp_key in expected:
            reg = re.compile('[^a-zA-Z]')
            if reg.sub('', key).lower() == exp_key:
                input[exp_key] = input.pop(key)
                break
