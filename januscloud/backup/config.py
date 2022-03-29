# -*- coding: utf-8 -*-
from januscloud.common.schema import Schema, StrVal, Default, AutoDel, Optional, BoolVal, IntVal, \
    StrRe, EnumVal, Or, DoNotCare
from januscloud.common.confparser import parse as parse_config
import os
# import logging

# log = logging.getLogger(__name__)

config_schema = Schema({
    Optional("general"): Default({
        Optional("daemonize"): Default(BoolVal(), default=False),
        AutoDel(str): object  # for all other key we don't care
    }, default={}),

    Optional("janus"): Default({
        Optional("queue_name"): Default(StrVal(min_len=0, max_len=64), default=''),
        Optional("mux_api_token"): Default(StrVal(min_len=0, max_len=64), default=''),
        Optional("mux_api_secret"): Default(StrVal(min_len=0, max_len=255), default=''),
        Optional("recordings_dir"): Default(StrVal(min_len=0, max_len=255), default=''),
        Optional("max_recording_seconds"): Default(IntVal(min=0, max=86400), default=120),
        Optional("redis_connection"): Default(StrVal(min_len=0, max_len=255), default=''),
        AutoDel(str): object  # for all other key remove
    }, default={}),
    Optional("proc_watcher"): Default({
        Optional("cmdline"): Default(StrVal(), default=''),
        Optional("error_restart_interval"): Default(IntVal(min=0, max=86400), default=10),
        Optional("poll_interval"): Default(IntVal(min=1, max=3600), default=1),
        AutoDel(str): object  # for all other key remove
    }, default={}),
})


def load_conf(path):
    if path is None or path == '':
        config = config_schema.validate({})
    else:
        print('Janus-sentinel-backup loads the config file: {}'.format(os.path.abspath(path)))
        config = parse_config(path, config_schema)

    # check other configure option is valid or not
    # TODO

    return config


if __name__ == '__main__':
    conf = config_schema.validate({})
    import pprint
    pprint.pprint(conf)
