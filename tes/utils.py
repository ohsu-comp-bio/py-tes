import simplejson as json
import re

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
        for k, v in m.iteritems():
            d[camel_to_snake(k)] = v
        return o(**d)
    else:
        return o(**m)
