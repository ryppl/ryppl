# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
import sys
import os

from ryppl.support._argparse import valid_0install_feed
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

def run(args):
    # Suppress all 0install GUI elements
    os.environ['DISPLAY']=''
    config = zeroinstall.injector.config.load_config()
    
    # Only download new feed information every hour unless otherwise
    # specified.  NOTE: You can raise this value, but lower values
    # will be ignored unless you also monkeypatch
    # zeroinstall.injector.iface_cache.FAILED_CHECK_DELAY
    config.freshness = 60*60

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

        import pprint
        pprint.pprint([(x[0],x[1].attrs) for x in driver.solver.selections.selections.items()])

if __name__ == '__main__':
    test()
