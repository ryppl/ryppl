# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
"""Supplies the main entry point for the ryppl command"""

import argparse
import commands
from commands import *

def run(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-commands')
    parser.add_argument('--verbose', action='store_true')

    for module_name in commands.__all__:
        cmd_module = getattr(commands, module_name)

        cmd_name = module_name.replace('_', '-')[int(module_name.startswith('_')):]

        kw = dict(description=getattr(cmd_module, '__doc__'))
        print kw

        subparser = subparsers.add_parser(cmd_name, **kw)
        subparser.set_defaults(runner=cmd_module.run)
        cmd_module.command_line_interface(subparser)

    parsed_args = parser.parse_args(argv[1:])
    parsed_args.runner(parsed_args)
    
