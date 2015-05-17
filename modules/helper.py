'''
Local helper methods
'''

import re
import hashlib

def __virtual__():
    return 'helper'

def regex_replace(s, find, replace):
    """A non-optimal implementation of a regex filter"""
    return re.sub(find, replace, s)

def regex_match(s, pattern):
    """A non-optimal implementation of a regex match"""
    return re.match(pattern, s)

def md5hash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

def throw(s):
    """Raise an error. Mostly usefull within jinja templates"""
    raise Exception(s)

def is_dict(o):
   """Test wether 'o' is a dict"""
   return isinstance(o, dict)
