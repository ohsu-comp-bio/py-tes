from __future__ import absolute_import, print_function

import json
import re

from requests import HTTPError


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def json2obj(j, o, convert_camel_case=True):
    if isinstance(j, str):
        m = json.loads(j)
    elif isinstance(j, dict):
        m = j
    else:
        raise TypeError("j must be a str or dict")
    if convert_camel_case:
        d = {}
        for k, v in m.items():
            d[camel_to_snake(k)] = v
        return o(**d)
    else:
        return o(**m)


def raise_for_status(response):
    try:
        response.raise_for_status()
    except HTTPError:
        raise HTTPError(
            "\n<status code> %d\n<response> %s\n" %
            (response.status_code, response.text)
        )
