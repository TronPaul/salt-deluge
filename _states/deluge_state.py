__virtualname__ = 'deluge'


def __virtual__():
    if 'deluge.get_config_value' in __salt__:
        return __virtualname__
    else:
        return False


def config_value(name, value, config_dir):
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    cv = __salt__['deluge.get_config_value'](name, config_dir)
    if cv != value:
        __salt__['deluge.set_config_value'](name, value, config_dir)
        ret['changes'][name] = {'old': cv, 'new': value}
        ret['comment'] = '{} changed from {} to {}'.format(name, cv, value)
        ret['result'] = True
    else:
        ret['comment'] = '{} was already set to {}'.format(name, value)
        ret['result'] = True
    return ret
