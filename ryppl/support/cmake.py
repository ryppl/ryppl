# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from ryppl.support import _zeroinstall
from logging import info
import subprocess
import os

cmake_2_8_10_plus = (
    '--not-before=2.8.10'
    , 'http://ryppl.github.com/feeds/cmake.xml')

command = _zeroinstall.launch_command + cmake_2_8_10_plus

def cmake(args, **kw):
    info('cmake-2.8.10+ %s', args)
    return _zeroinstall.launch(cmake_2_8_10_plus+tuple(args), **kw)

def configure_for_circular_dependencies(*args, **kw):
    info('CMake first pass')
    cmd = command + tuple(args)
    p = subprocess.Popen(
        cmd,
        stdout=open(os.devnull,'w'), 
        stderr=subprocess.PIPE, 
        **kw)
    stderr = p.communicate()[1]
    if p.wait() == 0 or 'Initial pass successfully completed, now run again!' not in stderr:
        raise subprocess.CalledProcessError(
            p.returncode, cmd,
            output=stderr if p.returncode  else
            'Expected to exit with an error after initial configuration pass\n' + stderr)

    info('CMake second pass')
    cmake(args, **kw)

def generators():
    help = subprocess.check_output(command + ('--help',))

    generator_block = help.split('The following generators are available on this platform:')[1]
    ret = []
    for line in generator_block.replace('\r\n','\n').split('\n'):
        if line.startswith('  ') and len(line) > 2 and not line.startswith('   '):
            g = line.split('=')[0].strip()
            if g:
                ret.append(g)
    return ret

if __name__ == '__main__':
    print generators()
    configure_for_circular_dependencies('-G', 'Xcode', '../src')

