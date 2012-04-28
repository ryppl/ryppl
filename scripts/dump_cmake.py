import os
import shutil
from tempdir import TempDir
from subprocess import Popen, PIPE, CalledProcessError
from path import Path

home = Path(os.environ['HOME'])
dump_dir = home / 'src' / 'ryppl' / 'feeds' / 'dumps'
boost_zero = home / 'src' / 'ryppl' / 'boost-zero'
modules = boost_zero / 'ryppl' / 'Modules'

if __name__ == '__main__':
    with TempDir() as build_dir:
        os.chdir(build_dir)
        env = os.environ.copy()
        env['PATH'] += os.pathsep + '/opt/local/lib/openmpi/bin'
        p = Popen(['cmake', '-DCMAKE_MODULE_PATH='+modules, '-DRYPPL_PROJECT_DUMP_DIRECTORY=' + dump_dir, boost_zero], env=env, 
                  stdout=open(os.devnull,'w'), stderr=PIPE)
        stderr = p.communicate()[1]
        assert p.returncode != 0, 'Expected to exit with an error after initial configuration pass'
        if not 'Initial pass successfully completed, now run again!' in stderr:
            print stderr
            raise CalledProcessError(p.returncode, 'cmake', output=stderr)
