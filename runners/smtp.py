# -*- coding: utf-8 -*-
'''
Runner frontend to smtp system
'''

# Import python libs
from __future__ import print_function
import time
import os
import copy
import logging

# Import Salt libs
import salt.client
import salt.output
import salt.pillar
import salt.utils
from salt.utils.odict import OrderedDict as _OrderedDict

log = logging.getLogger(__name__)

def send_msg(recipient,
        message,
        subject='Message from Salt',
        sender=None,
        server=None,
        use_ssl='True',
        usermessage=None,
        password=None,
        profile=None):
    '''
    This is the runner counterpart to module/state.smtp.send_msg

    '''

    ret = {'message': message,
           'subject': subject,
           'recipient': recipient,
           'changes': {},
           'result': None,
           'comment': ''}
    if  __opts__.get('test', False):
        ret['comment'] = 'Need to send message to {0}: {1}'.format(
            recipient,
            message,
        )
        return ret

    # TODO: Initialize pillar data..
    minion = salt.minion.MasterMinion(__opts__)

    #import IPython; IPython.embed_kernel();
    command = minion.functions['smtp.send_msg'](
        message=message,
        recipient=recipient,
        profile=profile,
        subject=subject,
        sender=sender,
        use_ssl=use_ssl,
    )

    if command:
        ret['result'] = True
        ret['comment'] = 'Sent message to {0}: {1}'.format(recipient, message)
    else:
        ret['result'] = False
        ret['comment'] = 'Unable to send message to {0}: {1}'.format(recipient, message)

    salt.output.display_output(ret, 'pprint', __opts__)
    return ret
