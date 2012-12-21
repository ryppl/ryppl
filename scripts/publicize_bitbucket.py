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

bitbucket_url = functools.partial(urlparse.urljoin, 'https://api.bitbucket.org/1.0/')

auth = 'Basic ' + sys.argv[1].encode('base64')

start_page = int( (sys.argv + ['1'])[2] )

repositories = json.loads(
    restclient.GET(
        bitbucket_url('user/repositories/'),
        headers=dict(Authorization=auth))
    )

for repo in repositories:
    if repo['owner'] == 'ryppl' and repo['is_private'] == True:
        
        # curl --request PUT -u 'user:pass' https://api.bitbucket.org/1.0/repositories/ryppl/python/ --data 'is_private=false'        
        print repo['name']
        put_result = restclient.PUT(
                bitbucket_url('repositories/ryppl/' + repo['slug']), 
                headers=dict(Authorization=auth),
                async=True,
                params=dict(
                    is_private=False
                    ),
                accept=['text/json']
            )

