# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import
import io

# Import 3rd-party libs
try:
    import six
except Exception:
    from salt.ext import six  # Fallback for Salt <3006

import salt.utils.files
from salt.utils.stringutils import to_str,to_bytes

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
	result = __salt__['nacl.dec_file'](name, out=out, **kwargs)

	if encoding:
		return to_str(result, encoding)

	return result

def enc_file(name, out=None, **kwargs):
    data = None
    try:
        return __salt__['enc_file'](name, out, **kwargs);
    except Exception as e:  # pylint: disable=broad-except
        # likly using salt-run so fallback to local filesystem
        with salt.utils.files.fopen(name, "rb") as f:
            data = to_bytes(f.read())
    d = __salt__['nacl.enc'](data, **kwargs)
    if out:
        if os.path.isfile(out):
            raise Exception("file:{} already exist.".format(out))
        with salt.utils.files.fopen(out, "wb") as f:
            f.write(to_bytes(d))
        return "Wrote: {}".format(out)
    return d


