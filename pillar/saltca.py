# -*- coding: utf-8 -*-
'''
Auto-generate hosts certificate & private key and expose them as pillar data.
'''

# Don't "fix" the above docstring to put it on two lines, as the sphinx
# autosummary pulls only the first line for its description.

# Import python libs
import copy
import ctypes
import os.path
import logging

try:
    from contextlib import nested
except ImportError:
    from contextlib import ExitStack, contextmanager

    @contextmanager
    def nested(*contexts):
        with ExitStack() as stack:
            for ctx in contexts:
                stack.enter_context(ctx)
            yield contexts

# Import salt libs
import salt.utils
from distutils.version import LooseVersion

HAS_SSL = False
X509_EXT_ENABLED = False
try:
    import OpenSSL
    HAS_SSL = True
    OpenSSL_version = LooseVersion(OpenSSL.__dict__.get('__version__', '0.0'))
except ImportError:
    pass

# Set up logging
log = logging.getLogger(__name__)
traverse_dict_and_list = None

if salt.version.__version__ >= '2018.3.0':
    traverse_dict_and_list = salt.utils.data.traverse_dict_and_list
else:
    traverse_dict_and_list = salt.utils.traverse_dict_and_list

# Options
__opts__ = {
    'saltca.pki.path': '/srv/salt/pki',
    'saltca.pki.name': 'hosts',
    'saltca.pki.C': 'US',
    'saltca.pki.ST': 'Utah',
    'saltca.pki.L': 'Salt Lake City',
    'saltca.pki.O': 'SaltStack',
    'saltca.pki.OU': None,
    'saltca.pki.emailAddress': None,
    'saltca.pki.days': 3650
}

def __init__( __opts__ ):

    global X509_EXT_ENABLED

    if HAS_SSL and OpenSSL_version >= LooseVersion('0.15'):
        X509_EXT_ENABLED = True

    return

def create_cert_for(host, opts):
    log.info('Generating certificate for: {0}'.format(host))
    cacert_path = opts['saltca.pki.path']
    pkiname = opts['saltca.pki.name']
    # tls.create_csr hosts cacert_path=/srv/salt/pki CN=sample.test.domain.com O=TESTCA emailAddress=support@test.com "subjectAltName=['DNS:sample.test.domain.com']"
    __salt__['tls.create_csr'](pkiname,
        cacert_path=cacert_path,
        cert_type='common',
        CN=host,
        C=opts['saltca.pki.C'],
        ST=opts['saltca.pki.ST'],
        L=opts['saltca.pki.L'],
        O=opts['saltca.pki.O'],
        OU=opts['saltca.pki.OU'],
        emailAddress=opts['saltca.pki.emailAddress'],
        subjectAltName=(['DNS:' + host] if X509_EXT_ENABLED else None)
    )
    # salt-call --local -l debug tls.create_ca_signed_cert hosts cacert_path=/srv/salt/pki CN=sample.test.domain.com days=3650
    __salt__['tls.create_ca_signed_cert'](pkiname,
        cacert_path=cacert_path,
        cert_type='common',
        CN=host,
        days=opts['saltca.pki.days']
    )

    return lookup_cert_for(host, opts)

def lookup_cert_for(host, opts):
    log.info('Looking up certificate for: %s' % host)
    cacert_path = opts['saltca.pki.path']
    pkiname = opts['saltca.pki.name']
    crtfile = '%s/%s/certs/%s.crt' % ( cacert_path, pkiname, host )
    keyfile = '%s/%s/certs/%s.key' % ( cacert_path, pkiname, host )

    if not os.path.isfile(crtfile) or not os.path.isfile(keyfile):
        return (None, None)

    with nested(open(crtfile), open(keyfile)) as (c, k):
        return (c.read(), k.read())

def ext_pillar(minion_id, pillar, caname=None, capath=None, attrs={}):
    '''
    Expose certificate & privKey as pillar items.
    '''
    res = {}
    host = minion_id
    opts = copy.deepcopy(__opts__)

    log.debug('Running with: {0} -- {1} -- {2}'.format(caname, capath, attrs))

    if traverse_dict_and_list(pillar, 'pki:saltca:disable', False):
        return res

    if caname != None: opts['saltca.pki.name'] = caname;
    if capath != None: opts['saltca.pki.path'] = capath;

    for attr in [ 'C', 'ST', 'L', 'O', 'OU', 'emailAddress' ]:
        if attr in attrs:
            opts['saltca.pki.' + attr] = attrs[attr]

    if traverse_dict_and_list(pillar, 'pki:certs:' + host, False):
        return res

    cert, key = lookup_cert_for(host, opts)

    if cert == None or key == None:
        phack = False
        if not 'pillar.get' in __salt__:
            # Ensure pillar.get is present while calling tls module
            phack = True
            __pillar__.update(pillar)
            __salt__['pillar.get'] = __pillar__.get
        try:
            cert, key = create_cert_for(host, opts)
        finally:
            if phack:
                __salt__.pop('pillar.get')

    if cert != None or key != None:
        data = res['pki'] = pillar['pki'] if 'pki' in pillar else {}
        certs = data['certs'] = data['certs'] if 'certs' in data else {}
        certs.update({ host: cert })
        privkeys = data['privkeys'] = data['privkeys'] if 'privkeys' in data else {}
        privkeys.update({ host: key })

    return res

#
# vim: set ai,ts=4,expandtab
#
