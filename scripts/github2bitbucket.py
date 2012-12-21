# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

# Mirror a bunch of Git repositories to bitbucket
#
# Invoke this script with one argument of the form
#
#   <bitbucket-username>:<bitbucket-password>
#
# to make this work, you need to install restclient, and you probably
# need to update the certificates in your httplib2.  For example, I
# copied the file used by curl from
# /opt/local/share/curl/curl-ca-bundle.crt into
# /Library/Python/2.7/site-packages/httplib2/cacerts.txt
#

import sys
import restclient
import urlparse
import functools
import argparse
import json
import pprint
import tempdir
import subprocess
import os

github_url = functools.partial(urlparse.urljoin, 'https://api.github.com')
bitbucket_url = functools.partial(urlparse.urljoin, 'https://api.bitbucket.org/1.0/')

auth = 'Basic ' + sys.argv[1].encode('base64')

start_page = int( (sys.argv + ['1'])[2] )

for page in range(start_page, 1000):

    print '#### PAGE', page

    repositories = json.loads(
        restclient.GET(
            github_url('/orgs/boost-lib/repos'), 
            params=dict(page=page)))

    for src_repo in repositories:
        clone_url = src_repo['clone_url']
        repo_name = src_repo['name']

        print repo_name+':'
        parent = tempdir.TempDir()
        subprocess.check_call(
            [ 'git', 'clone', '--quiet', '--mirror', clone_url ], cwd=parent)
        print '  cloned'

        post_result = restclient.POST(
                bitbucket_url('repositories/'), 
                headers=dict(Authorization=auth),
                async=False,
                params=dict(
                    name=repo_name,
                    description=src_repo['description'],
                    language=src_repo['language'].lower(),
                    website=(src_repo['homepage'] or 'http://boost.org/libs/' + repo_name),
                    scm='git', 
                    is_private='false',
                    owner='ryppl'
                    ),
                accept=['text/json']
            )

        try:
            json.loads(post_result)
        except:
            if not ' already has a repository with this name.' in post_result:
                raise Exception, post_result

        print '  created'

        repo_dotgit = repo_name + '.git'

        subprocess.check_call(
            [ 'git', 'remote', 'add', 'bitbucket', 'git@bitbucket.org:ryppl/' + repo_dotgit],
            cwd=os.path.join(parent, repo_dotgit)
            )

        subprocess.check_call(
            [ 'git', 'push', '--quiet', '--mirror', 'bitbucket'],
            cwd=os.path.join(parent, repo_dotgit)
            )
        print '  pushed'
        since = src_repo['id']

