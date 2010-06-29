# -*- coding: utf-8 -*-
"""
A very thin wrapper on top of the FluidDB RESTful API

Copyright (c) 2009-2010 Seo Sanghyeon, Nicholas Tollervey and others

See README, AUTHORS and LICENSE for more information
"""

import sys
import httplib2
import urllib
import numbers
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

def call(method, path, body=None, mime=None, **kw):
    """
    Makes a call to FluidDB

    method = HTTP verb. e.g. PUT, POST, GET, DELETE or HEAD
    path = Path appended to the instance to locate the resource in FluidDB
    body = The request body (a dictionary will be translated to json,
    primitive types will also be jsonified)
    mime = The mime-type for the body of the request - will override the
    jsonification of primitive types
    **kw = Query-string arguments to be appended to the URL
    """
    http = httplib2.Http()
    url = instance + urllib.quote(path)
    if kw:
        url = url + '?' + urllib.urlencode(kw)
    headers = global_headers.copy()
    # Make sure the correct content-type header is sent
    if isinstance(body, dict):
        # jsonify dicts
        headers['content-type'] = 'application/json'
        body = json.dumps(body, ensure_ascii=False)
    elif method.upper() == 'PUT' and path.startswith('/objects/'):
        # A PUT to an "/objects/" resource means that we're handling 
        # tag-values. Make sure we handle primitive/opaque value types
        # properly.
        if mime:
            # opaque value (just set the mime type)
            headers['content-type'] = mime
        elif isprimitive(body):
            # primitive values need to be json-ified and have the correct
            # content-type set
            headers['content-type'] = 'application/vnd.fluiddb.value+json'
            body = json.dumps(body, ensure_ascii=False)
        else:
            # No way to work out what content-type to send to FluidDB so
            # bail out.
            raise TypeError("You must supply a mime-type")
    response, content = http.request(url, method, body, headers)
    if ((response['content-type'] == 'application/json' or
        response['content-type'] == 'application/vnd.fluiddb.value+json')
        and content):
        result = json.loads(content)
    else:
        result = content
    return response, result

def isprimitive(body):
    """
    Given the body of a request will return a boolean to indicate if the
    value is a primitive value type.

    See:

    http://doc.fluidinfo.com/fluidDB/api/tag-values.html
    &
    http://doc.fluidinfo.com/fluidDB/api/http.html#payloads-containing-tag-values

    For an explanation of the difference between primitive and opaque
    values.
    """
    if (isinstance(body, numbers.Number) or isinstance(body, basestring) or
           isinstance(body, bool) or body == None):
        return True
    elif isinstance(body, list):
        # Check the list contains only strings. 
        for item in body:
            if not isinstance(item, basestring):
                return False
        return True
    else:
        return False
