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

def _error(ret, err_msg):
    ret['result'] = False
    ret['comment'] = err_msg
    return ret

def send_msg(recipient,
        message,
        subject='Message from Salt',
        sender=None,
        use_ssl='True',
        profile=None,
        template=None,
        context={}):
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
    local_minion_opts = __opts__.copy()
    local_minion_opts['file_client'] = 'local'
    minion = salt.minion.MasterMinion(local_minion_opts)

    if template != None:
        tmplfn = minion.functions['cp.get_template'](
            message,
            '',
            template=template,
            context=context
        )
        msg = 'cp.get_template returned {0} (Called with: {1})'
        log.debug(msg.format(tmplfn, message))
        if tmplfn:
            tmplines = None
            with salt.utils.fopen(tmplfn, 'rb') as fp_:
                tmplines = fp_.readlines()
            if not tmplines:
                msg = 'Failed to read rendered template file {0} ({1})'
                log.debug(msg.format(tmplfn, message))
		raise ValueError(msg.format(tmplfn, message))
            message = ''.join(tmplines)
        else:
            msg = 'Failed to load template file {0}'.format(message)
            log.debug(msg)
            raise ValueError(msg)

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
