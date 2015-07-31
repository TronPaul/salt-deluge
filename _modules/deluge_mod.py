# -*- coding: utf-8 -*-
'''
Execution module to provide deluge configuration to Salt
.. versionadded:: 2015.8.0
'''
from salt.exceptions import CommandExecutionError


ERROR = 'The key {} is invalid!'


__virtualname__ = 'deluge'


def __virtual__():
    '''
    Only load if deluge libraries exist.
    '''
    if not __salt__['cmd.has_exec']('deluge-console'):
        return False
    else:
        return __virtualname__


def get_config_value(key, config_dir):
    res = __salt__['cmd.run_all']('deluge-console -c {} config {}'.format(config_dir, key)
    return res['stdout']

def set_config_value(key, value, config_dir):
    __salt__['cmd.run_all']('deluge-console -c {} config {}'.format(config_dir, key)
    if 'Configuration value successfully updated.' in res['stdout']:
        return True
    else:
        return False
