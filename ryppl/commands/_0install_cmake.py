# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
'''Used in 0install feeds for building CMake-based Ryppl projects from source'''

def command_line_interface(cli):
    """Defines the command-line interface for this module's sub-command"""
    cli.add_argument(
        '--overlay'
      , help='A directory to be overlaid on the composite source directory before building')

    cli.add_argument(
        '--add-subdirectory', nargs=2, action='append', metavar=('SOURCEDIR','SUBDIR')
      , help='''Copy SOURCEDIR into SUBDIR of the composite source
 directory and generate a top-level CMakeLists.txt file that includes
 it.  This is sometimes necessary to handle evil dependency
 clusters.'''
        )

    cli.add_argument(
        '--build-type', default='Release'
      , help='Passed to CMake with -DCMAKE_BUILD_TYPE=%(metavar)s'
        )

    cli.add_argument(
        'components'
      , nargs='+'
      , help='''The CMake components to be built.  If subdirectories have
been added with --add-subdirectory, each component should be
prefixed by its subdirectory and a slash, e.g. "regex/dev".''')

def run(args):
    print args

