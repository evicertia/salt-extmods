'''
Rendering State module.
'''

# Import python libs
import logging
import collections

# Import third party libs
import yaml

# Import salt libs
import salt.utils
from salt._compat import string_types

log = logging.getLogger(__name__)

_state = {}

def __virtual__():
    return 'rendstate'

def clear():
   """Clears render state"""
   global _state
   _state = {}

def items():
   return _state

def update(dict):
   _state.update(dict)

def get(key, default='', delimiter=':'):
   return salt.utils.traverse_dict_and_list(_state, key, default, delimiter)


