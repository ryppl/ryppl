import tempfile
import os
import shutil

class TempDir(object):
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def __enter__(self):
        self.dir = tempfile.mkdtemp(*self.args, **self.kw)
        self.saved_wd = os.getcwd()
        return self.dir

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.saved_wd)
        try:
            shutil.rmtree(self.dir)
        except:
            print 'failed to clean up', self.dir
            pass # we don't care very much if it doesn't get cleaned up

