# -*- coding: utf-8 -*-

# Import 3rd-party libs
import salt.utils.nacl
import salt.utils.files
from salt.utils.stringutils import to_str,to_bytes

REQ_ERROR = None
try:
   import salt.utils.nacl
   salt.utils.nacl.check_requirements()
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

def enc_file(name, out=None, **kwargs):
    data = None
    try:
        kwargs["opts"] = __opts__
        return salt.utils.nacl.enc_file(name, out, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
        # likly using salt-run so fallback to local filesystem
        with salt.utils.files.fopen(name, "rb") as f:
            data = to_bytes(f.read())
    d = salt.utils.nacl.enc(data, **kwargs)
    if out:
        if os.path.isfile(out):
            raise Exception("file:{} already exist.".format(out))
        with salt.utils.files.fopen(out, "wb") as f:
            f.write(to_bytes(d))
        return "Wrote: {}".format(out)
    return d


