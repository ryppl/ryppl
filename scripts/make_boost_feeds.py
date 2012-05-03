# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt

import glob, os, sys
from datetime import date, datetime
from warnings import warn
from subprocess import check_output
from xml.etree.cElementTree import ElementTree, Element
from dom import dashtag, xml_document, xmlns
from path import Path
import boost_metadata
from uuid import uuid4 as make_uuid
from archive import Archive
from sign_feed import *
import threadpool
from read_dumps import read_dumps
_ = dashtag

package_prefixes = ['Boost', 'Ryppl']
def split_package_prefix(package_name):
    for prefix in package_prefixes:
        n = len(prefix)
        if (len(package_name) > n
            and package_name.startswith(prefix)
            and package_name[n].isupper()):
            return prefix, package_name[n:]
    return None, package_name

class GenerateBoost(object):

    def cmake_package_to_feed_uri(self, cmake_package_name, component):
        prefix, basename = split_package_prefix(cmake_package_name)

        dump = self.dumps.get(cmake_package_name)
        repo = (dump.findtext('source-directory') - self.source_root) if dump else basename.lower()
        
        return 'http://ryppl.github.com/feeds/%s%s%s.xml' \
            % (
                  (prefix.lower() + '/' if prefix else '')
                , repo
                , ('' if component == 'bin' else '-'+component)
              )

    class GenerateRepo(object):
                
        def __getattr__(self, name):
            return getattr(self.ctx,name)

        def __init__(self, ctx, cmake_name):
            self.ctx = ctx
            self.cmake_name = cmake_name
            self.cmake_dump = self.dumps[cmake_name]
            self.srcdir = self.cmake_dump.findtext('source-directory')
            self.git_revision = check_output(['git', 'rev-parse', 'HEAD'], cwd=self.srcdir).strip()
            self.repo = str(self.srcdir - self.source_root)
            self.boost_metadata = boost_metadata.lib_metadata(self.repo, self.boost_metadata)
            self.has_binaries = cmake_name in self.binary_libs
            prefix,self.feed_name_base = split_package_prefix(cmake_name)
            self.brand_name = prefix + '.' + self.feed_name_base if prefix else self.feed_name_base

            print '##', self.brand_name

            self.tasks.add_task(self._write_src_feed)
            if self.has_binaries:
                self._write_preinstall_feed()
            self.tasks.add_task(self._write_dev_feed)
        
        def _feed_name(self, component):
            return self.repo + ('' if component == 'bin' else '-'+component) + '.xml'
            
        def _write_feed(self, component, *contents):
            interface = self._interface(component)[ 
                _.group(license=self._BSL_1_0) [
                    contents 
                ]
            ]
            interface.indent()
            feed_path = self.feed_dir/self._feed_name(component)
            xml_document(interface).write(feed_path, encoding='utf-8', xml_declaration=True)
            sign_feed(feed_path)

        def _feed_uri(self, component):
            return 'http://ryppl.github.com/feeds/boost/'+self._feed_name(component)

        _human_component = {
            'bin':'binaries'
            , 'src':'source code'
            , 'dev':'development files'
            , 'dbg':'debugging version'
            , 'preinstall':'built state'
            , 'doc':'documentation'
            }

        _boost_icon_png='http://svn.boost.org/svn/boost/website/public_html/live/gfx/boost-dark-trans.png'

        def _interface(self, component):
            interface = _.interface(
                uri=self._feed_uri(component)
              , xmlns='http://zero-install.sourceforge.net/2004/injector/interface'
              , **{
                    'xmlns:compile':'http://zero-install.sourceforge.net/2006/namespaces/0compile'
                  , 'xmlns:dc':'http://purl.org/dc/elements/1.1/'
                    })[
                _.name['%s (%s)' % (self.brand_name, self._human_component[component])]
              , _.icon(href=self._boost_icon_png, type="image/png")
              ]

            # These tags can be dragged directly across from our lib_metadata
            for tag in 'summary','homepage','dc:author','description','category':
                interface <<= self.boost_metadata.findall(tag)

            return interface

        def _implementation(self, arch):
            return _.implementation(
                arch=arch, id=make_uuid(), released=date.today().isoformat(), 
                stability='testing', version=self.version)

        def _git_snapshot(self, arch):
            git_revision = check_output(['git', 'rev-parse', 'HEAD'], cwd=self.srcdir).strip()
            archive_uri = 'http://nodeload.github.com/boost-lib/' + self.repo + '/zipball/' + git_revision
            zipball = Archive(archive_uri, self.repo, git_revision)

            return self._implementation(arch) [
                _.archive(extract=zipball.subdir, href=archive_uri, size=zipball.size, type='application/zip')
              , _.manifest_digest(sha1new=zipball.digest)
            ]

        _empty_zipball = (
            _.archive(
                extract='empty', href='http://ryppl.github.com/feeds/empty.zip'
              , size=162, type="application/zip"
            ), 
            _.manifest_digest(sha1new='da39a3ee5e6b4b0d3255bfef95601890afd80709')
            )


        _BSL_1_0 = 'OSI Approved :: Boost Software License 1.0 (BSL-1.0)'
        def _write_src_feed(self):
            self._write_feed(
                'src'
               , self._git_snapshot('*-*')
                )

        def _cmakelists_overlay(self):
            return _.requires(interface='http://ryppl.github.com/feeds/boost/CMakeLists.xml')[
                _.environment(insert=self.repo, mode='replace', name='BOOST_CMAKELISTS_OVERLAY')
            ]
            
        def _write_dev_feed(self):
            if self.cmake_name in self.binary_libs:
                return  # don't know what to do for this case yet

            self._write_feed(
                'dev'
              , self._implementation('*-src') [
                    self._empty_zipball
                    ]
              , _.command(name='compile') [
                    self.0cmake_runner( 'dev' if self.has_binaries else 'headers' )
                  , _.requires(
                        interface=self._feed_uri('preinstall' if self.has_binaries else 'src')
                    ) [
                        _.environment(insert='.', mode='replace', name='SRCDIR')
                    ]
                  , self._cmakelists_overlay()
                  , xmlns.compile.implementation(arch='*-*')
              ]
          )

        def _write_preinstall_feed(self):
            self._write_feed(
                'preinstall'
              , self._implementation('*-src') [
                    self._empty_zipball
                    ]
              , _.command(name='compile') [
                    _.runner(interface='http://ryppl.github.com/feeds/ryppl/0cmake.xml') [
                        _.version(**{'not-before':'0.8-pre-201205011504'})
                      , _.arg[ 'preinstall' ]
                    ]
                  , _.requires(interface=self._feed_uri('src')) [
                        _.environment(insert='.', mode='replace', name='SRCDIR')
                    ]
                  , self._cmakelists_overlay()
                  , self._build_requirements()
              ]
          )

        def _build_requirements(self):
            """Return a set of (feedURI, CMakeVariable) pairs that can
            be used to generate build requirements"""
            requirements = []
            for fp in (
                self.cmake_dump.findall('find-package')
              + self.cmake_dump.findall('find-package-indirect')):
                cmake_package = fp.find('arg').text

                # Dumps currently can contain self-loops; we have to
                # eliminate those or 0compile loops infinitely.  
                if cmake_package != self.cmake_name:
                    feed_uri = self.cmake_package_to_feed_uri(cmake_package, 'dev')
                    requirements.append(
                        _.requires(interface=feed_uri) [
                            _.environment(insert='.', mode='replace', name=cmake_package+'_DIR')
                        ]
                    )
            return requirements


    def _delete_old_feeds(self):
        print '### deleting old feeds...'
        for old_feed in glob.glob(os.path.join(self.feed_dir,'*.xml')):
            if Path(old_feed).name != 'CMakeLists.xml':
                os.unlink(old_feed)

    def _identify_binary_libs(self):
        print '### identifying binary libraries:'
        self.binary_libs = set(
            name for name, dump in self.dumps.items() 
            if dump.find('libraries/library') is not None)

        import pprint
        pprint.pprint(self.binary_libs)

    def _check_for_modularity_errors(self):
        print '### Checking for modularity violations... ',
        from SCC import SCC

        def successors(v):
            return set(
                fp.findtext('arg') 
                for fp in self.dumps.get(v, Element('x')).findall('find-package')
            ) | set(
                fp.findtext('arg') 
                for fp in self.dumps.get(v, Element('x')).findall('find-package-indirect'))
        
        sccs = SCC(str,successors).getsccs(self.dumps)
        long_sccs = [s for s in sccs if len(s) > 1]

        if any(long_sccs):
            warn( 
            'Build dependency graph contains cycles.  All SCCs:\n'
            + repr(long_sccs))

        print 'Done.'

    def __init__(self, dump_dir, feed_dir, source_root, site_metadata_file):
        self.dump_dir = dump_dir
        self.feed_dir = feed_dir
        self.source_root = source_root

        self.dumps = read_dumps(self.dump_dir)

        # Make sure there are no modularity violations
        self._check_for_modularity_errors()
        
        self._identify_binary_libs()

        self.version = '1.49-post-' + datetime.utcnow().strftime("%Y%m%d%H%M")
        print '### new version =', self.version

        print '### reading Boost library metadata...'
        t = ElementTree()
        t.parse(site_metadata_file)
        self.boost_metadata = t.getroot().findall('library')

        self._delete_old_feeds()
        self.tasks = threadpool.ThreadPool(8)

        for cmake_name in self.dumps:
            self.GenerateRepo(self, cmake_name)

        print '### Awaiting completion...'
        self.tasks.wait_completion()
        print '### Done.'

if __name__ == '__main__':
    argv = sys.argv

    ryppl = Path('/Users/dave/src/ryppl')
    feeds = ryppl / 'feeds'
    lib_db_default = '/Users/dave/src/boost/svn/website/public_html/live/doc/libraries.xml'

    GenerateBoost(dump_dir=Path(argv[1] if len(argv) > 1 else feeds/'dumps')
      , feed_dir=Path(argv[2] if len(argv) > 2 else feeds/'boost')
      , source_root=Path(argv[3] if len(argv) > 3 else ryppl/'boost-zero'/'boost')
      , site_metadata_file=Path(argv[4] if len(argv) > 4 else lib_db_default)
        )
