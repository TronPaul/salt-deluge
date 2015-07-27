# -*- coding: utf-8 -*-
'''
Execution module to provide deluge configuration to Salt
.. versionadded:: 2015.8.0
'''
from salt.defaults import DEFAULT_TARGET_DELIM

try:
    # welcome to callback hell
    from twisted.internet import reactor
    from deluge.ui.client import client
    HAS_DELUGE = True
except ImportError:
    HAS_DELUGE = False

def __virtual__():
    '''
    Only load if deluge libraries exist.
    '''
    if not HAS_DELUGE:
        return False
    else:
        return 'deluge'

def _close_conn():
    client.disconnect()
    reactor.stop()

def _run_conn():
    reactor.run()

def _set_nested_config_value(client, key, value, delimiter, f):
    keys = key.split(delimiter)
    def on_get_config_value(top_level_value, key):
        data = top_level_value
        for each in keys[1:-1]:
            data = data[each]
        data[keys[-1]] = value
        config.set_config(keys[0], top_level_value).addCallback(f)
    client.core.get_config_value(key).addCallback(on_get_config_value, key)


def _set_config_value(client, key, value, f):
    client.core.set_config({key: value}).addCallback(f)


def get_config_value(key, delimiter=DEFAULT_TARGET_DELIM, host='127.0.0.1', port=58846, username=None, password=None):
    # Wishing nonlocal were here
    rv = {}
    def on_completion(value):
        if delimiter in key:
            rv['rv'] = traverse_dict(value, key.split(':', 1)[1], None, delimiter)
        else:
            rv['rv'] = value
        _close_conn()
    c = client.connect(host=host, port=port, username=username, password=password)
    def on_connect(*args):
        client.core.get_config_value(key).addCallback(on_completion)
    c.addCallback(on_connect)
    def on_fail(result):
        rv['error'] = result
        _close_conn()
    c.addErrback(on_fail)
    _run_conn()
    if 'rv' in rv:
        return rv['rv']
    #else:
    #???


def set_config_value(key, value, delimiter=DEFAULT_TARGET_DELIM, host='127.0.0.1', port=58846, username=None, password=None):
    rv = {}
    def on_completion(*args):
        rv['rv'] = True
        _close_conn()
    c = client.connect(host=host, port=port, username=username, password=password)
    def on_connect(*args):
        if delimiter in key:
            _set_nested_config_value(c, key, value, delimiter, on_completion)
        else:
            _set_config_value(c, key, value, on_completion)
    c.addCallback(on_connect)
    def on_fail(result):
        rv['error'] = result
        _close_conn()
    c.addErrback(on_fail)
    _run_conn()
