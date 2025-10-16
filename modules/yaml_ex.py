# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import
import io

# Import 3rd-party libs
import yaml
try:
    import six
except Exception:
    from salt.ext import six  # Fallback for Salt <3006

def yaml_dquote(text, split=True):
    '''
    Make text into a double-quoted YAML string with correct escaping
    for special characters.  Includes the opening and closing double
    quote characters.
    '''
    with io.StringIO() as ostream:
        yemitter = yaml.emitter.Emitter(ostream)
        yemitter.write_double_quoted(six.text_type(text), split)
        return ostream.getvalue()


def yaml_squote(text, split=True):
    '''
    Make text into a single-quoted YAML string with correct escaping
    for special characters.  Includes the opening and closing single
    quote characters.
    '''
    with io.StringIO() as ostream:
        yemitter = yaml.emitter.Emitter(ostream)
        yemitter.write_single_quoted(six.text_type(text), split)
        return ostream.getvalue()


def yaml_encode(data):
    '''
    A simple YAML encode that can take a single-element datatype and return
    a string representation.
    '''
    yrepr = yaml.representer.SafeRepresenter()
    ynode = yrepr.represent_data(data)
    if not isinstance(ynode, yaml.ScalarNode):
        raise TypeError(
            "yaml_encode() only works with YAML scalar data;"
            " failed for {0}".format(type(data))
        )

    tag = ynode.tag.rsplit(':', 1)[-1]
    ret = ynode.value

    if tag == "str":
        ret = yaml_dquote(ynode.value)

    return ret
