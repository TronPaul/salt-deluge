# -*- coding: utf-8 -*-
'''
Execution module to provide deluge configuration to Salt
.. versionadded:: 2015.8.0
'''
from salt.defaults import DEFAULT_TARGET_DELIM
from salt.exceptions import CommandExecutionError


try:
    # welcome to callback hell
    from twisted.internet import reactor
    from deluge.ui.client import client
    import deluge.configmanager
    from deluge.ui.common import get_localhost_auth
    HAS_DELUGE = True
except ImportError:
    HAS_DELUGE = False


__virtualname__ = 'deluge'


def __virtual__():
    '''
    Only load if deluge libraries exist.
    '''
    if not HAS_DELUGE:
        return False
    else:
        return __virtualname__


def _get_auth(config_dir):
    deluge.configmanager.set_config_dir(config_dir)
    return get_localhost_auth()


def _close_conn():
    client.disconnect()
    reactor.stop()


def _run_conn():
    reactor.run()


def _set_nested_config_value(key, value, delimiter, f):
    keys = key.split(delimiter)
    def on_get_config_value(top_level_value, key):
        data = top_level_value
        for each in keys[1:-1]:
            data = data[each]
        data[keys[-1]] = value
        config.set_config(keys[0], top_level_value).addCallback(f)
    client.core.get_config_value(key).addCallback(on_get_config_value, key)


def _set_config_value(key, value, f):
    client.core.set_config({key: value}).addCallback(f)


def get_config_value(key, config_dir=None, delimiter=DEFAULT_TARGET_DELIM):
    # Wishing nonlocal were here
    rv = {}
    username, password = _get_auth(config_dir)
    def on_completion(value):
        if delimiter in key:
            rv['rv'] = traverse_dict(value, key.split(':', 1)[1], None, delimiter)
        else:
            rv['rv'] = value
        _close_conn()
    d = client.connect(username=username, password=password)
    def on_connect(*args):
        client.core.get_config_value(key).addCallback(on_completion)
    d.addCallback(on_connect)
    def on_fail(result):
        rv['error'] = result
        _close_conn()
    d.addErrback(on_fail)
    _run_conn()
    if 'rv' in rv:
        return rv['rv']
    elif 'error' in rv:
        raise CommandExecutionError(rv['error'])
    else:
        raise CommandExecutionError('Something unexpected ocurred')


def set_config_value(key, value, config_dir=None, delimiter=DEFAULT_TARGET_DELIM):
    # Wishing nonlocal were here
    rv = {}
    username, password = _get_auth(config_dir)
    def on_completion(*args):
        rv['rv'] = True
        _close_conn()
    d = client.connect(username=username, password=password)
    def on_connect(*args):
        if delimiter in key:
            _set_nested_config_value(key, value, delimiter, on_completion)
        else:
            _set_config_value(key, value, on_completion)
    d.addCallback(on_connect)
    def on_fail(result):
        rv['error'] = result
        _close_conn()
    d.addErrback(on_fail)
    _run_conn()
    if 'rv' in rv:
        return rv['rv']
    elif 'error' in rv:
        raise CommandExecutionError(rv['error'])
    else:
        raise CommandExecutionError('Something unexpected ocurred')
