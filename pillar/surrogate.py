# -*- coding: utf-8 -*-
'''
Invokes a raw 'salt-call --pillar-root=/... pillar.items' returning surrogate results.
This pillar module is mainly intended to be used as a workaround when using salt in 
masterless within our vagrant sandbox. (pruiz)
'''
from __future__ import absolute_import

# Don't "fix" the above docstring to put it on two lines, as the sphinx
# autosummary pulls only the first line for its description.

# Import python libs
import logging
import json
import sys
from salt.utils.odict import OrderedDict
import salt.ext.six as six
from salt.ext.six import string_types
from salt.ext.six.moves import range

# Set up logging
log = logging.getLogger(__name__)
command = 'salt-call -l quiet --local -c /etc/salt/empty --out=json --pillar-root={0} pillar.items'

def ext_pillar(minion_id,  # pylint: disable=W0613
               pillar,  # pylint: disable=W0613
               path):
    '''
    Execute a command and read the output as JSON
    '''
    try:
        log.info('fetching pillar data for {0}.'.format(minion_id))
        # TODO: Use spawn in order to fetch stderr and log it.
        data = __salt__['cmd.run'](command.format(path))
        return _result_unicode_to_utf8(json.loads(data)['local'])
    except Exception:
        log.critical(
                'JSON data from {0} failed to parse: {1}'.format(command, sys.exc_info())
                )
        return {}

def _result_unicode_to_utf8(data):
    ''''
    Replace `unicode` strings by utf-8 `str` in final yaml result

    This is a recursive function
    '''
    #log.warning(' ==> KKKKKK: {0}'.format(type(data)))
    if isinstance(data, OrderedDict):
        for key, elt in six.iteritems(data):
            data.pop(key)
            data[key.encode('utf-8')] = _result_unicode_to_utf8(elt)
    elif isinstance(data, dict):
        for key, elt in six.iteritems(data):
            data.pop(key)
            data[key.encode('utf-8')] = _result_unicode_to_utf8(elt)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = _result_unicode_to_utf8(data[i])
    elif isinstance(data, six.text_type):
        # here also
        data = data.encode('utf-8')
    return data

# vim: set ai,ts=4,expandtab
