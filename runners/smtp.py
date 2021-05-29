# -*- coding: utf-8 -*-
'''
Runner frontend to smtp system
'''

# Import python libs
from __future__ import print_function
import time
import os
import copy
import socket
import logging

import smtplib
import email.mime.text

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

def _send_msg(recipient,
        message,
        subject='Message from Salt',
        sender=None,
        server=None,
        use_ssl='True',
        username=None,
        password=None,
        profile=None,
        subtype='plain'):
    '''
    Send a message to an SMTP recipient. Designed for use in states.

    CLI Examples::

        smtp.send_msg 'admin@example.com' 'This is a salt module test' \
            profile='my-smtp-account'
        smtp.send_msg 'admin@example.com' 'This is a salt module test' \
            username='myuser' password='verybadpass' sender="admin@example.com' \
            server='smtp.domain.com'
    '''
    if profile:
        conf_file = __opts__['conf_file']
        opts = salt.config.client_config(conf_file)
        #creds = __salt__['config.option'](profile)
        creds = opts[profile]
        server = creds.get('smtp.server')
        use_ssl = creds.get('smtp.tls')
        sender = creds.get('smtp.sender')
        username = creds.get('smtp.username')
        password = creds.get('smtp.password')

    msg = email.mime.text.MIMEText(message, subtype)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        if use_ssl in ['True', 'true']:
            smtpconn = smtplib.SMTP_SSL(server)
        else:
            smtpconn = smtplib.SMTP(server)

    except socket.gaierror as _error:
        log.debug("Exception: {0}" . format(_error))
        return False

    if use_ssl not in ('True', 'true'):
        smtpconn.ehlo()
        if smtpconn.has_extn('STARTTLS'):
            try:
                smtpconn.starttls()
            except smtplib.SMTPHeloError:
                log.debug("The server didn’t reply properly \
                        to the HELO greeting.")
                return False
            except smtplib.SMTPException:
                log.debug("The server does not support the STARTTLS extension.")
                return False
            except RuntimeError:
                log.debug("SSL/TLS support is not available \
                        to your Python interpreter.")
                return False
            smtpconn.ehlo()

    if username and password:
        try:
            smtpconn.login(username, password)
        except smtplib.SMTPAuthenticationError as _error:
            log.debug("SMTP Authentication Failure")
            return False

    try:
        smtpconn.sendmail(sender, [recipient], msg.as_string())
    except smtplib.SMTPRecipientsRefused:
        log.debug("All recipients were refused.")
        return False
    except smtplib.SMTPHeloError:
        log.debug("The server didn’t reply properly to the HELO greeting.")
        return False
    except smtplib.SMTPSenderRefused:
        log.debug("The server didn’t accept the {0}.".format(sender))
        return False
    except smtplib.SMTPDataError:
        log.debug("The server replied with an unexpected error code.")
        return False

    smtpconn.quit()
    return True

def send_msg(recipient,
        message,
        subject='Message from Salt',
        sender=None,
        use_ssl='True',
        profile=None,
        subtype=None,
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

    #command = minion.functions['smtp_ex.send_msg'](
    command = _send_msg(
        message=message,
        recipient=recipient,
        profile=profile,
        subject=subject,
        sender=sender,
        use_ssl=use_ssl,
        subtype=subtype
    )

    if command:
        ret['result'] = True
        ret['comment'] = 'Sent message to {0}: {1}'.format(recipient, message)
    else:
        ret['result'] = False
        ret['comment'] = 'Unable to send message to {0}: {1}'.format(recipient, message)

    salt.output.display_output(ret, 'pprint', __opts__)
    return ret
