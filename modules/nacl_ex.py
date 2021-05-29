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
    """
    Alias to `{box_type}_decrypt`

    box_type: secretbox, sealedbox(default)
    """
    kwargs["opts"] = __opts__
    result = salt.modules.nacl.dec(data, **kwargs)
    encoding = kwargs.get("encoding")

    if encoding:
        return to_str(result, encoding)

    return result
