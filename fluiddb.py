# -*- coding: utf-8 -*-
"""
A very thin wrapper on top of the FluidDB RESTful API

Copyright (c) 2009-2010 Seo Sanghyeon, Nicholas Tollervey and others

See README, AUTHORS and LICENSE for more information
"""

import sys
import httplib2
import urllib
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# There are currently two instances of FluidDB. MAIN is the default standard
# instance and SANDBOX is a scratch version for testing purposes. Data in
# SANDBOX can (and will) be blown away.
MAIN = 'https://fluiddb.fluidinfo.com'
SANDBOX = 'https://sandbox.fluidinfo.com'
instance = MAIN

global_headers = {
    'Accept': '*/*',
}

def login(username, password):
    """
    Creates the 'Authorization' token from the given username and password.
    """
    userpass = username + ':' + password
    auth = 'Basic ' + userpass.encode('base64').strip()
    global_headers['Authorization'] = auth

def logout():
    """
    Removes the 'Authorization' token from the headers passed into FluidDB
    """
    if global_headers.has_key('Authorization'):
        del global_headers['Authorization']

def call(method, path, body=None, mime='text/plain', **kw):
    """
    Makes a call to FluidDB

    method = HTTP verb. e.g. PUT, POST, GET, DELETE or HEAD
    path = Path appended to the instance to locate the resource in FluidDB
    body = The request body (a dictionary will be translated to json)
    mime = The mime-type for the body of the request
    **kw = Query-string arguments to be appended to the URL
    """
    http = httplib2.Http()
    url = instance + urllib.quote(path)
    if kw:
        url = url + '?' + urllib.urlencode(kw)
    headers = global_headers.copy()
    if isinstance(body, dict):
        headers['content-type'] = 'application/json'
        body = json.dumps(body)
    elif body:
        headers['content-type'] = mime
    response, content = http.request(url, method, body, headers)
    if response['content-type'].startswith('application/json'):
        result = json.loads(content)
    else:
        result = content
    return response, result
