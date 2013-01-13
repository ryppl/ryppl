# Copyright Dave Abrahams 2012. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

# Fork repositories from one GitHub org to another.
#
# Invoke this script with one argument of the form
#
#   <github-username>:<github-password>
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
import json
from cStringIO import StringIO

def github_url(*elements):
    return urlparse.urljoin('https://api.github.com', '/'.join(elements))

def encode_auth(username_colon_password):
    return 'Basic ' + username_colon_password.encode('base64')

src_org = 'boost-lib'
dst_org = 'boostorg'

src_auth = None
if len(sys.argv) > 2:
    src_auth = encode_auth(sys.argv[2])

dst_auth = encode_auth(sys.argv[1])

class Headers(dict):
    '''A dictionary of RFC2822 internet message headers

When you initialize it with keywords, any underscores are replaced
with dashes, for example:

>>> Headers(Content_Type='application/json')
{'Content-Type': 'application/json'}
'''
    def __init__(self, **kw):
        dict.__init__(
            self,
            ((k.replace('_','-'),v) for (k,v) in kw.items()))
            
def list_github_repos(org, auth=None):
    return json.loads(
        restclient.GET(
            github_url('orgs', org, 'repos'),
            headers=auth and dict(Authorization=auth),
            params=dict(per_page=1000)))

src_repositories = list_github_repos('boost-lib')
dst_repositories = list_github_repos('boostorg')

for src_repo in src_repositories:
    repo_name = src_repo['name']

    post_result = restclient.POST(
            github_url('repos', src_org, repo_name, 'forks'), 
            headers=Headers(Authorization=dst_auth, Content_Type='application/json'),
            params=dict(organization=dst_org),
            async=False,
            accept=['text/json']
            )
    try:
        result = json.loads(post_result)
    except Exception, e:
        raise e, post_result

    print '  forked', repo_name

