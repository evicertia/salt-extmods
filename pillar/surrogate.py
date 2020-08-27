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
import subprocess
from salt.utils.odict import OrderedDict
import salt.ext.six as six
from salt.ext.six import string_types
from salt.ext.six.moves import range

# Set up logging
log = logging.getLogger(__name__)
saltcmd = [ 'salt-call', '-l', 'quiet', '--local', '--out=json' ]

def ext_pillar(minion_id,  # pylint: disable=W0613
               pillar,  # pylint: disable=W0613
               utf8fix=False,
               root=None,
               modules=None,
               configdir=None):
    '''
    Execute a command and read the output as JSON
    '''
    try:
        log.info('==> fetching pillar data for {0} [utf8fix: {1}].'.format(minion_id, utf8fix))

	    params = { 'config-dir': '/etc/salt/surrogate' }
        if root is not None: params['pillar-root'] = root
        if modules is not None: params['module-dir'] = modules
        if configdir is not None: params['config-dir'] = configdir

        args = map(lambda (key, value): "--{0}='{1}'".format(key, value), params.iteritems())
        command = saltcmd + args + [ 'pillar.items' ]
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = child.communicate()
        if child.returncode != 0 or (err != None and len(err) > 0):
            log.error('Surrogate pillar error: {0}'.format(err))
        data = json.loads(unicode(output))
        return (_result_unicode_to_utf8(data) if utf8fix else data)['local']
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
