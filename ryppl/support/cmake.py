# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from ryppl.support import _zeroinstall
from logging import info
import subprocess
import os

cmake_2_8_8_plus = (
    '--not-before=2.8.8'
    , 'https://raw.github.com/ryppl/feeds/gh-pages/cmake.xml')

command = _zeroinstall.launch_command + cmake_2_8_8_plus

def cmake(args, **kw):
    info('cmake-2.8.8+ %s', args)
    return _zeroinstall.launch(cmake_2_8_8_plus+args, **kw)

def configure_for_circular_dependencies(*args, **kw):
    info('CMake first pass')
    cmd = command + tuple(args)
    p = subprocess.Popen(
        cmd,
        stdout=open(os.devnull,'w'), 
        stderr=subprocess.PIPE, 
        **kw)
    stderr = p.communicate()[1]
    if p.returncode == 0 or 'Initial pass successfully completed, now run again!' not in stderr:
        raise subprocess.CalledProcessError(
            p.returncode, cmd,
            output=stderr if p.returncode  else
            'Expected to exit with an error after initial configuration pass')

    info('CMake second pass')
    cmake(args, **kw)

def generators():
    help = subprocess.check_output(command + ('--help',))

    generator_block = help.split('''
Generators

The following generators are available on this platform:
''')[1]
    ret = []
    for line in generator_block.split('\n'):
        g = line.split('=')[0].strip()
        if g:
            ret.append(g)
    return ret

if __name__ == '__main__':
    print generators()
    configure_for_circular_dependencies('-G', 'Xcode', '../src')

