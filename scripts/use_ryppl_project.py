import glob, re, os
from warnings import warn
from xml.etree.ElementTree import ElementTree
lib_db = ElementTree()
lib_db.parse('/Users/dave/src/boost/svn/website/public_html/live/doc/libraries.xml')

libraries = lib_db.findall('library')

project_decl = re.compile(r'(?<!\w)project\((?P<name>\w+)\s*(?P<languages>[^)]*)\)')
listfile_root = '/Users/dave/src/ryppl/boost-zero/cmake/'

def quoted(s):
    return '"' + s.replace('\\', '\\\\').replace('"','\\"').replace(';', ':') + '"'

for root,dirs,files in os.walk(listfile_root):

    if 'CMakeLists.txt' in files:
        listfile_dir = root[len(listfile_root):]
        listfile_path = os.path.join(root, 'CMakeLists.txt')

        libs = [
            l for l in libraries 
            if l.findtext('key') == listfile_dir
            or l.findtext('key').startswith(listfile_dir+'/') ]
            
        with open(listfile_path) as f:
            contents = f.read()
            m = project_decl.search(contents)
            
        if m:
            if len(libs) == 0:
                print '*** No metadata found in libraries.xml for library path %s' % listfile_dir
            elif len(libs) > 1:
                print '--- Merging metadata for %s into library path %s' % (
                    [l.findtext('key') for l in libs]
                    , listfile_dir)

            with open(listfile_path, 'w') as f:
                f.write(contents[:m.start()])
                f.write('include(RypplProject)\n')
                f.write('ryppl_project(' + m.group('name'))
                
                languages = m.group('languages').strip()

                if languages in ('', 'NONE'):
                    f.write(' HEADER_ONLY')
                    languages = None
                
                summary = '***WRITE ME (one line)***'
                description = None
                if len(libs) > 0:
                    id = libs[0].findtext('key').split('/')[0] 
                else:
                    id = m.group('name').lower()

                for l in libs:
                    if l.findtext('key') == id:
                        summary = re.sub(r'\s+', ' ', l.findtext('description'))

                if len(libs) > 1:
                    description = '\n\n'.join([l.findtext('key') + ':\n' + l.findtext('description') for l in libs])

                f.write('\n  FEED_URI http://ryppl.github.com/feeds/boost/%s.xml' % id)

                f.write('\n  SUMMARY ' + quoted(summary))

                if description:
                    f.write('\n  DESCRIPTION\n  ' + quoted(description))
                else:
                    f.write('\n  # DESCRIPTION\n  # "Write a full (possibly multi-paragraph) description here"')

                f.write('\n  HOMEPAGE "http://boost.org/' 
                        + ''.join([l.findtext('documentation') for l in libs][:1])
                        + '"'.encode('utf-8'))

                authors = set()
                for l in libs:
                    a0 = re.split('\s*(?:(?:,\s*(?:and\s+)?)|(?:and\s+))', l.findtext('authors'))
                    for a in a0:
                        authors.add(quoted(re.sub(r'\s+', ' ', a)).encode('utf-8'))
                f.write('\n  AUTHOR ' + ' '.join(authors))
                f.write('\n  MAINTAINER ' + ' '.join(authors))

                f.write('\n  CATEGORY Development')

                keywords = set()
                for l in libs:
                    for c in l.findall('category'):
                        keywords.add(c.text)
                f.write('\n  KEYWORDS "Boost" ' + ' '.join([quoted(k) for k in keywords]).encode('utf-8'))
                f.write(
                    '\n  ICON' 
                    ' "http://svn.boost.org/svn/boost/website/public_html/live/gfx/boost-dark-trans.png"'
                    ' "image/png"')
                if languages:
                    f.write('\n  CMAKE_LANGUAGES ' + languages)
                f.write('\n)')
                f.write(contents[m.end():])
        else:
            assert len(libs) == 0
            # print 'no project in', listfile_dir, libs
