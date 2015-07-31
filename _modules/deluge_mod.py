# -*- coding: utf-8 -*-
'''
Execution module to provide deluge configuration to Salt
.. versionadded:: 2015.8.0
'''
import re
from salt.exceptions import CommandExecutionError


ERROR = 'The key {} is invalid!'
RET_RE = '^\s*{}: (?P<value>.*)$'


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
    res = __salt__['cmd.run_all']('deluge-console -c {} config {}'.format(config_dir, key))
    if 'Failed to connect' in res['stdout']:
        raise CommandExecutionError(res['stdout'])
    else:
        pattern = RET_RE.format(key)
        return re.match(pattern, res['stdout']).group('value')

def set_config_value(key, value, config_dir):
    res = __salt__['cmd.run_all']('deluge-console -c {} config -s {} {}'.format(config_dir, key, value))
    if 'Configuration value successfully updated.' in res['stdout']:
        return True
    else:
        raise CommandExecutionError(res['stdout'])
