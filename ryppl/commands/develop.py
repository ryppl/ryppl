# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
import sys
import os

from ryppl.support.path import *
from ryppl.support._argparse import valid_0install_feed, creatable_path
import zeroinstall.injector.requirements
import zeroinstall.injector.config
import zeroinstall.injector.driver

def command_line_interface(cli):
    '''Set up a project workspace for the given feeds'''

    import zeroinstall.injector.model
    cli.add_argument(
        '--refresh'
        , action='store_true'
        , help='Force 0install to update its cached feeds now')

    cli.add_argument(
        'feed'
        , nargs = '+'
        , type=valid_0install_feed
        , help='0install feed of Ryppl project to develop')

    cli.add_argument(
        'workspace'
        , nargs=1
        , type=creatable_path
        , help='Path to project workspace directory, which must not already exist')

def solve(args, config):
    selections = None
    versions = {}
    for iface_uri in args.feed:
        requirements = zeroinstall.injector.requirements.Requirements(iface_uri)
        requirements.command = 'develop'
        
	driver = zeroinstall.injector.driver.Driver(
            config=config, requirements=requirements)

        refresh = args.refresh
        if not refresh:
            # Note that need_download() triggers a solve
            driver.need_download()
            refresh = any(
                feed for feed in driver.solver.feeds_used if
                # Ignore (memory-only) PackageKit feeds
                not feed.startswith('distribution:') and
                config.iface_cache.is_stale(feed, config.freshness))

        blocker = driver.solve_with_downloads(refresh)
        if blocker:
            zeroinstall.support.tasks.wait_for_blocker(blocker)

        if not driver.solver.ready:
            raise driver.solver.get_failure_reason()

        if not selections:
            selections = driver.solver.selections
        else:
            for uri,sel in driver.solver.selections.selections.items():
                v = versions.setdefault(uri, sel.attrs['version'])
                assert v == sel.attrs['version'], 'Version mismatch; not yet supported.'
                selections.selections[uri] = sel
    return selections

def git_clone_feed(feed, tree_ish, where, id, config):
    print feed.get_name()# , where, feed.metadata, feed.implementations[id]
    for x in feed.metadata:
        print x
    print


def generate(args, selections, config):
    workspace = args.workspace[0]
    dep_dir = workspace/'.dependencies'
    os.makedirs(dep_dir)

    for uri,sel in selections.selections.items():
        feed = config.iface_cache.get_feed(uri)
        if feed.implementations.get(sel.id):
            git_clone_feed(
                feed
                , sel.attrs['version']
                , workspace if uri in args.feed else dep_dir
                , sel.id
                , config)
            

def run(args):
    # Suppress all 0install GUI elements
    os.environ['DISPLAY']=''

    config = zeroinstall.injector.config.load_config()
    # Only download new feed information every hour unless otherwise
    # specified.  NOTE: You can raise this value, but lower values
    # will be ignored unless you also monkeypatch
    # zeroinstall.injector.iface_cache.FAILED_CHECK_DELAY
    config.freshness = 60*60
    
    selections = solve(args, config)
    generate(args, selections, config)

