#!/usr/bin/env python3
# encoding: utf-8

import os, argparse
import pkg_resources

from .configmanager import CONFIG_MANAGER
from .conky_keep import build_notes
from .build_conkyrc import build_conkyrc

def main():
    # get path to app dir
    path = os.path.dirname(os.path.abspath(__file__))

    # init config
    default_conf_path = pkg_resources.resource_filename(__name__, "config_default.cfg")
    CONFIG_MANAGER.loadConfig(default_conf_path)

    # get config file path - config file in same folder has higher priority
    conf_file = "config.cfg"
    # config in same folder as conkyKeep.sh (../)
    if os.path.isfile(os.path.join(path, '..', conf_file)):
        conf_path = os.path.join(path, '..', conf_file)
    # config in ~/.config/conkykeep folder
    else:
        try:
            import appdirs
            app_config_dir = appdirs.user_config_dir('conkykeep')
        except:
            app_config_dir = os.path.join(os.path.expanduser("~"), '.config', 'conkykeep')
        conf_path = os.path.join(app_config_dir, conf_file)

    # load user config
    if not os.path.isfile(conf_path):
        print("ERROR: config file not found in: %s" % (conf_path,))
    else:
        CONFIG_MANAGER.loadConfig(conf_path)

    # parse commandline args
    parser = argparse.ArgumentParser(description='ConkyKeep')
    parser.add_argument('--buildconkyrc', '-c', default=None,
                        help='Builds new conkyrc in on given path and exits')
    parser.add_argument('--buildnotes', '-n', action='store_true',
                        help='Builds note images and prints conky syntax for displaying them')
    args = parser.parse_args()

    # build notes or conkyrc
    if args.buildconkyrc is not None:
        build_conkyrc(args.buildconkyrc)
    elif args.buildnotes:
        build_notes()

main()

