# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import
import io

# Import 3rd-party libs
import salt.ext.six as six
from salt.utils.stringutils import to_str

REQ_ERROR = None
try:
   import salt.modules.nacl
except (ImportError, OSError) as e:
   REQ_ERROR = True


__virtualname__ = 'nacl_ex'

def __virtual__():
    '''
    Only load if nacl is available.
    '''
    if REQ_ERROR:
        return False
    return True

def dec(data, **kwargs):
    encoding = kwargs.pop("encoding", None)
    result = __salt__['nacl.dec'](data, **kwargs)

    if encoding:
        return to_str(result, encoding)

    return result

def dec_file(name, out=None, **kwargs):
	encoding = kwargs.pop("encoding", None)
	result = __salt__['nacl.dec_file'](data, out=out, **kwargs)

	if encoding:
		return to_str(result, encoding)

	return result
