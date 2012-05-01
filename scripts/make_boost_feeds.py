# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt

import glob, re, os, sys, shutil, urllib2
from datetime import date, datetime
from warnings import warn
from subprocess import check_output, check_call, Popen, PIPE
from xml.etree.cElementTree import ElementTree, Element
import dom, path
from path import Path
import boost_metadata
from uuid import uuid4 as make_uuid
from archive import Archive
from sign_feed import *
import threadpool

def content_length(uri):
    request = urllib2.Request(uri)
    request.get_method = lambda : 'HEAD'
    response = urllib2.urlopen(request)
    length = response.info().get('content-length')
    if length:
        return int(length)
    else:
        return len(urllib2.urlopen(uri).read())

package_prefixes = ['Boost', 'Ryppl']
def split_package_prefix(package_name):
    for prefix in package_prefixes:
        n = len(prefix)
        if (len(package_name) > n
            and package_name.startswith(prefix)
            and package_name[n].isupper()):
            return prefix, package_name[n:]
    return None, package_name

def requirement(package_name):
    prefix, basename = split_package_prefix(package_name)
    return (
        'http://ryppl.github.com/feeds/%s%s-dev.xml'
        % ((prefix.lower() + '/' if prefix else ''), basename)
      , package_name + '_DIR')

def get_build_requirements(cmake_dump):
    requirements = set()
    for fp in cmake_dump.findall('find-package'):
        args = fp.findall('arg')
        requirements.add(requirement(args[0].text))

    return sorted(requirements)

def interface_head(
    uri, brand_name, component, 
    icon_png="http://svn.boost.org/svn/boost/website/public_html/live/gfx/boost-dark-trans.png"):

    human_component = {
        'bin':'binaries'
      , 'src':'source code'
      , 'dev':'development files'
      , 'dbg':'debugging version'
      , 'preinstall':'built state'
      , 'doc':'documentation'
        }

    _ = dom.dashtag
    return _.interface(
        uri=uri
      , xmlns='http://zero-install.sourceforge.net/2004/injector/interface'
      , **{
            'xmlns:compile':'http://zero-install.sourceforge.net/2006/namespaces/0compile'
          , 'xmlns:dc':'http://purl.org/dc/elements/1.1/'
            })[
        _.name['%s (%s)' % (brand_name, human_component[component])]
      , _.icon(href=icon_png, type="image/png")
      ]


def boost_interface_head(repo, brand_name, component):
    return interface_head('http://ryppl.github.com/feeds/boost/%s.xml'%repo, brand_name, component)

def boost_group(version, arch):
    _ = dom.dashtag
    return _.group(license='OSI Approved :: Boost Software License 1.0 (BSL-1.0)')[
        _.implementation(arch=arch
                          , id=str(make_uuid())
                          , released=date.today().isoformat()
                          , stability='testing'
                          , version=version
                            )
        ]

def boost_archive(repo, git_dir):
    git_revision = check_output(['git', 'rev-parse', 'HEAD'], cwd=git_dir).strip()
    archive_uri = 'http://nodeload.github.com/boost-lib/' + repo + '/zipball/' + git_revision
    z = Archive(archive_uri, repo, git_revision)

    _ = dom.dashtag
    return ( 
        _.archive(extract=z.subdir, href=archive_uri, size=str(z.size), type='application/zip')
      , _.manifest_digest(sha1new=z.digest)
    )

def compile_command(component, repo_name):
    _ = dom.dashtag
    return _.command(name='compile') [
            _.runner(interface='http://ryppl.github.com/feeds/ryppl/0cmake.xml')
            [
                _.version(**{'not-before':'0.8-pre-201204291303'})
              , _.arg[ '--component='+component ]
              , _.arg[ '--overlay=${BOOST_CMAKELISTS_OVERLAY}' ] if component == 'preinstall' else []
            ]
          , _.requires(interface='http://ryppl.github.com/feeds/boost/CMakeLists.xml')[
                _.environment(insert=repo_name, mode='replace', name='BOOST_CMAKELISTS_OVERLAY')
            ] if component == 'preinstall' else []

          , [  _.requires(interface=uri)[ _.environment(insert='.', mode='replace', name=var) ]
                for uri,var in build_requirements ]
          , [ dom.xmlns.compile.implementation(arch='*-*')
              if component == 'dev' and not cmake_dump.findall('libraries/library')
              else [] ]
        ]

def write_feed(cmake_dump, feed_dir, repo_name, camel_name, component, lib_metadata, version):
    build_requirements = get_build_requirements(cmake_dump)
    lib_name = os.path.basename(srcdir)

    prefix,feed_name_base = split_package_prefix(camel_name)
    brand_name = prefix + '.' + feed_name_base if prefix else feed_name_base

    suffix = '-%s'%component if component != 'bin' else ''
    feed_name = feed_name_base + suffix + '.xml'

    # prepare the header of the root element
    iface = interface_head(
        'http://ryppl.github.com/feeds/boost/' + feed_name
      , brand_name, component)

    # These tags can be dragged directly across from our lib_metadata
    for tag in 'summary','homepage','dc:author','description','category':
        iface <<= lib_metadata.findall(tag)

    arch = '*-*' if component in ['src'] else '*-src'
    # arch = '*-src'

    group = boost_group(
        repo_name, 
        git_dir=cmake_dump.findtext('source-directory'), 
        arch=arch, version=version)
    if component == 'src':
        group <<= boost_archive(repo_name, srcdir, )

    if arch == '*-src':
        group <<= compile_command(component)

    iface <<= group

    iface.indent()

    feed_path = feed_dir/feed_name
    dom.xml_document(iface).write(feed_path, encoding='utf-8', xml_declaration=True)

    sign_feed(feed_path)


class Generate(object):

    class GenerateRepo(object):
        def __init__(self, ctx, cmake_name):
            self.ctx = ctx
            self.cmake_name = cmake_name
            self.cmake_dump = self.dumps[cmake_name]
            self.srcdir = self.cmake_dump.findtext('source-directory')
            self.git_revision = check_output(['git', 'rev-parse', 'HEAD'], cwd=self.srcdir).strip()
            self.repo = str(self.srcdir - self.source_root)
            self.boost_metadata = boost_metadata.lib_metadata(self.repo, self.boost_metadata)

            prefix,self.feed_name_base = split_package_prefix(cmake_name)
            self.brand_name = prefix + '.' + self.feed_name_base if prefix else self.feed_name_base

            print '##', self.brand_name

            self.tasks.add_task(self._write_src_feed)
            if cmake_name in self.binary_libs:
                self._write_binary_feeds()
            else:
                self._write_header_only_feeds()
        
        def __getattr__(self, name):
            return getattr(self.ctx,name)

        def _write_feed(self, component, interface):
            interface.indent()
            feed_path = self.feed_dir/self.repo + ('' if component == 'bin' else '-'+component) + '.xml'
            dom.xml_document(interface).write(feed_path, encoding='utf-8', xml_declaration=True)
            sign_feed(feed_path)

        def _interface(self, component):
            interface = interface_head('http://ryppl.github.com/feeds/boost/%s.xml'%self.repo, self.brand_name, component)
            
            # These tags can be dragged directly across from our lib_metadata
            for tag in 'summary','homepage','dc:author','description','category':
                interface <<= self.boost_metadata.findall(tag)

            return interface

        def _write_src_feed(self):
            self._write_feed(
                'src'
                , self._interface('src') [
                    boost_group(version=self.version, arch='*-*')[
                        boost_archive(self.repo, self.srcdir)
                        ]
                    ]
                )

        def _write_dev_feed(self):
            if cmake_name in self.binary_libs:
                return  # don't know what to do for this case yet

            self._write_feed(
                'dev'
                , self._interface('dev') [
                    boost_group(version=self.version, arch='*-src')[
                        
                        ]
                    ]
                )
                    

        def _write_binary_feeds(self):
            pass

    def _delete_old_feeds(self):
        print '### deleting old feeds...'
        for old_feed in glob.glob(os.path.join(self.feed_dir,'*.xml')):
            if Path(old_feed).name != 'CMakeLists.xml':
                os.unlink(old_feed)

    def _read_dumps(self):
        print '### collecting all dumps...'
        self.dumps = {}
        for cmake_dump_file in glob.glob(os.path.join(self.dump_dir,'*.xml')):
            cmake_dump = ElementTree()
            cmake_dump.parse(cmake_dump_file)
            camel_name = Path(cmake_dump_file).namebase
            self.dumps[camel_name] = cmake_dump

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
            return set([
                    fp.findtext('arg') for fp
                    in (
                        self.dumps.get(v, Element('x')).findall('find-package')
                        + self.dumps.get(v, Element('x')).findall('find-package-indirect')
                        )
                    ])
        
        sccs = SCC(str,successors).getsccs(self.dumps.keys())

        if len(sccs) < len(self.dumps):
            raise AssertionError, ( 
            'Build dependency graph contains cycles.  All SCCs:\n'
            + repr(s for s in sccs if len(s) > 1))

        print 'Done.'

    def __init__(self, dump_dir, feed_dir, source_root, site_metadata_file):
        self.dump_dir = dump_dir
        self.feed_dir = feed_dir
        self.source_root = source_root

        self._read_dumps()

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

    Generate(dump_dir=Path(argv[1] if len(argv) > 1 else feeds/'dumps')
      , feed_dir=Path(argv[2] if len(argv) > 2 else feeds/'boost')
      , source_root=Path(argv[3] if len(argv) > 3 else ryppl/'boost-zero'/'boost')
      , site_metadata_file=Path(argv[4] if len(argv) > 4 else lib_db_default)
        )
