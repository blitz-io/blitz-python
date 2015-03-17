__author__="ghermeto"
__date__ ="$28/07/2011 19:13:12$"

import re
try: 
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def validate_url(url):
    parsed = urlparse(url)
    return parsed.scheme and parsed.netloc

def validate_int(value):
    str_value = str(value)
    return True if re.search("^[0-9]+$", str_value) else False

def validate_list(lst):
    return isinstance(lst, list) or isinstance(lst, tuple)

def validate(options):
    failed = []
    if not 'steps' in options or not validate_list(options['steps']):
        failed.append('steps')
    else:
        step = options['steps'][0]
        if not 'url' in step or not validate_url(step['url']):
            failed.append('url')

        for step in options['steps']:
            if 'referrer' in step and not validate_url(step['referrer']):
                failed.append('referrer')
            if 'status' in step and not validate_int(step['status']):
                failed.append('status')
            if 'timeout' in step and not validate_int(step['timeout']):
                failed.append('timeout')
            if 'cookies' in step and not validate_list(step['cookies']):
                failed.append('cookies')
            if 'headers' in step and not validate_list(step['headers']):
                failed.append('headers')
    return failed
        