# Copyright (C) 2012 Dave Abrahams <dave@boostpro.com>
#
# Distributed under the Boost Software License, Version 1.0.  See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt

import glob, re, os, sys, shutil, tempfile, urllib2
from datetime import date, datetime
from warnings import warn
from subprocess import check_output, Popen, PIPE
from xml.etree.cElementTree import ElementTree
import dom, path
from path import Path
import boost_metadata
from uuid import uuid4 as make_uuid

def content_length(uri):
    request = urllib2.Request(uri)
    request.get_method = lambda : 'HEAD'
    response = urllib2.urlopen(request)
    length = response.info().get('content-length')
    if length:
        return int(length)
    else:
        return len(urllib2.urlopen(uri).read())

def get_build_requirements(cmake_dump):
    requirements = []
    for fp in cmake_dump.findall('find-package'):
        args = fp.findall('arg')
        if args[0].text == 'Boost' and args[1].text == 'COMPONENTS' and args[-1].text == 'NO_MODULE':
            for a in args[2:-1]:
                feed_base = ''.join(x.capitalize() for x in a.text.split('_'))
                
                requirements.append(
                    ( 'http://ryppl.github.com/feeds/boost/%s-dev.xml' % feed_base
                      , 'Boost%s_DIR' % feed_base
                      )
                    )
        else:
            print '========>', dom.tostring(fp)

    return requirements

def write_feed(cmake_dump, feed_dir, source_subdir, camel_name, component, lib_metadata):
    # os.unlink(feed_file)
    build_requirements = get_build_requirements(cmake_dump)
    srcdir = cmake_dump.findtext('source-directory')
    lib_name = os.path.basename(srcdir)
    lib_revision = check_output(['git', 'rev-parse', 'HEAD'], cwd=srcdir).strip()

    version = '1.49-post-' + datetime.utcnow().strftime("%Y%m%d%H%M")
    feed_name_base = camel_name[len('Boost') if camel_name.startswith('Boost') else 0:]

    suffix = '-%s'%component if component != 'bin' else ''
    feed_name = feed_name_base + suffix + '.xml'

    # prepare the header of the root element
    _ = dom.dashtag
    iface = _.interface(
        uri='http://ryppl.github.com/feeds/boost/' + feed_name
      , xmlns='http://zero-install.sourceforge.net/2004/injector/interface'
      , **{ 
            'xmlns:compile':'http://zero-install.sourceforge.net/2006/namespaces/0compile'
          , 'xmlns:dc':'http://purl.org/dc/elements/1.1/'
            })[
        _.name[camel_name]
      , _.icon(href="http://svn.boost.org/svn/boost/website/public_html/live/gfx/boost-dark-trans.png" 
             , type="image/png")
      ]

    # These tags can be dragged directly across from our lib_metadata
    for tag in 'summary','homepage','dc:author','description','category':
        iface <<= lib_metadata.findall(tag)

    archive_uri = 'http://nodeload.github.com/boost-lib/' + source_subdir + '/zipball/' + lib_revision

    cmake = lambda s: [
        _.arg[x] for x in 
        ['http://afb.users.sourceforge.net/zero-install/interfaces/cmake.xml'] + s.split()
        ]
    
    semi = _.arg[';']

    iface <<= _.group(license='OSI Approved :: Boost Software License 1.0 (BSL-1.0)')[
        _.implementation(arch='*-src'
                          , id=str(make_uuid())
                          , released=date.today().isoformat()
                          , stability='testing'
                          , version=version
                            )
           [
               _.archive(extract='boost-lib-' + source_subdir + '-' + lib_revision[:7]
                       , href=archive_uri
                       , size=str(content_length(archive_uri))
                       , type='application/zip')
               ]
      , _.command(name='compile')
        [
            _.runner(interface='http://ryppl.github.com/feeds/ryppl/0runner.xml')
            [
                cmake('-E copy_directory ${SRCDIR} ./source'
                      + ''.join(' -D%s=%s'%(var,var) for uri,var in build_requirements)), semi
              , cmake('-E copy_directory ${BOOST_CMAKELISTS_DIR}/%s ./source' % source_subdir), semi
              , cmake('./source' +  # configure
                      {'dbg':' -DBUILD_TYPE=Debug ', 'bin':' -DBUILD_TYPE=Release '}.get(component,'')
                      ), semi
              , cmake('--build .' + (' --target documentation' if component == 'doc' else '')), semi
              , cmake('-DCOMPONENT=%s -DCMAKE_INSTALL_PREFIX=${DISTDIR} -P cmake_install.cmake' % component)
            ]
          , _.requires(interface='http://ryppl.github.com/feeds/boost/cmakelists.xml')[
                _.environment(insert='.', mode='replace', name='BOOST_CMAKELISTS_DIR')
            ]
          , [  _.requires(interface=uri)[ _.environment(insert='.', mode='replace', name=var) ]
                for uri,var in build_requirements ]
        ]
    ]
    
    print 20*'#' + ' ' + source_subdir + ' ' + 20*'#'
    print iface

def run(dump_dir, feed_dir, source_root, site_metadata_file):
    t = ElementTree()
    t.parse(site_metadata_file)
    all_libs_metadata = t.getroot().findall('library')

    for cmake_dump_file in glob.glob(os.path.join(dump_dir,'*.xml')):
        
        camel_name = Path(cmake_dump_file).namebase
        cmake_dump = ElementTree()
        cmake_dump.parse(cmake_dump_file)

        source_subdir = cmake_dump.findtext('source-directory') - source_root
        lib_metadata = boost_metadata.lib_metadata(source_subdir, all_libs_metadata)

        write_feed(cmake_dump, feed_dir, source_subdir, camel_name, 'dev', lib_metadata)

        if (cmake_dump.find('libraries/library')):
            write_feed(cmake_dump, feed_dir, source_subdir, camel_name, 'bin', lib_metadata)

        write_feed(cmake_dump, feed_dir, source_subdir, camel_name, 'dbg', lib_metadata)
        

if __name__ == '__main__':
    argv = sys.argv

    ryppl = Path('/Users/dave/src/ryppl')
    feeds = ryppl / 'feeds'
    lib_db_default = '/Users/dave/src/boost/svn/website/public_html/live/doc/libraries.xml'

    run(dump_dir=Path(argv[1] if len(argv) > 1 else feeds/'dumps')
      , feed_dir=Path(argv[2] if len(argv) > 2 else feeds/'boost')
      , source_root=Path(argv[3] if len(argv) > 3 else ryppl/'boost-zero'/'boost')
      , site_metadata_file=Path(argv[4] if len(argv) > 4 else lib_db_default)
        )
