# -*- coding: utf-8 -*-
"""
A very thin wrapper on top of the Fluidinfo RESTful API

Copyright (c) 2009-2010 Seo Sanghyeon, Nicholas Tollervey and others

See README, AUTHORS and LICENSE for more information
"""

import sys
import requests
import urllib
import types
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json


# There are currently two instances of Fluidinfo. MAIN is the default standard
# instance and SANDBOX is a scratch version for testing purposes. Data in
# SANDBOX can (and will) be blown away.
MAIN = 'https://fluiddb.fluidinfo.com'
SANDBOX = 'https://sandbox.fluidinfo.com'
instance = MAIN


ITERABLE_TYPES = set((list, tuple))
SERIALIZABLE_TYPES = set((types.NoneType, bool, int, float, str, unicode, list,
                          tuple))


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
    Removes the 'Authorization' token from the headers passed into Fluidinfo
    """
    if 'Authorization' in global_headers:
        del global_headers['Authorization']


def get(path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Convenience method for fluidinfo.call('GET', ...)
    """
    return call('GET', path, body, mime, tags, custom_headers, **kw)


def post(path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Convenience method for fluidinfo.call('POST', ...)
    """
    return call('POST', path, body, mime, tags, custom_headers, **kw)


def put(path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Convenience method for fluidinfo.call('PUT', ...)
    """
    return call('PUT', path, body, mime, tags, custom_headers, **kw)


def delete(path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Convenience method for fluidinfo.call('DELETE', ...)
    """
    return call('DELETE', path, body, mime, tags, custom_headers, **kw)


def head(path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Convenience method for fluidinfo.call('HEAD', ...)
    """
    return call('HEAD', path, body, mime, tags, custom_headers, **kw)


def call(method, path, body=None, mime=None, tags=[], custom_headers={}, **kw):
    """
    Makes a call to Fluidinfo

    method = HTTP verb. e.g. PUT, POST, GET, DELETE or HEAD
    path = Path appended to the instance to locate the resource in Fluidinfo
        this can be either a string OR a list of path elements.
    body = The request body (a dictionary will be translated to json,
        primitive types will also be jsonified)
    mime = The mime-type for the body of the request - will override the
        jsonification of primitive types
    tags = The list of tags to return if the request is to values
    headers = A dictionary containing additional headers to send in the request
    **kw = Query-string arguments to be appended to the URL
    """
    # build the URL
    url = build_url(path)
    if kw:
        url = url + '?' + urllib.urlencode(kw)
    if tags and path.startswith('/values'):
        # /values based requests must have a tags list to append to the
        # url args (which are passed in as **kw), so append them so everything
        # gets urlencoded correctly below
        url = url + '&' + urllib.urlencode([('tag', tag) for tag in tags])
    # set the headers
    headers = global_headers.copy()
    if custom_headers:
        headers.update(custom_headers)
    # make sure the path is a string for the following elif check for PUT
    # based requests
    if isinstance(path, list):
        path = '/'+'/'.join(path)
    # Make sure the correct content-type header is sent
    if isinstance(body, dict):
        # jsonify dicts
        headers['content-type'] = 'application/json'
        body = json.dumps(body)
    elif method.upper() == 'PUT' and (
        path.startswith('/objects/') or path.startswith('/about')):
        # A PUT to an "/objects/" or "/about/" resource means that we're
        # handling tag-values. Make sure we handle primitive/opaque value types
        # properly.
        if mime:
            # opaque value (just set the mime type)
            headers['content-type'] = mime
        elif isprimitive(body):
            # primitive values need to be json-ified and have the correct
            # content-type set
            headers['content-type'] = 'application/vnd.fluiddb.value+json'
            body = json.dumps(body)
        else:
            # No way to work out what content-type to send to Fluidinfo so
            # bail out.
            raise TypeError("You must supply a mime-type")
    response = requests.request(method, url, data=body, headers=headers)
    if ((response.headers['content-type'] == 'application/json' or
        response.headers['content-type'] == 'application/' +
            'vnd.fluiddb.value+json')
        and response.text):
        result = json.loads(response.text)
    else:
        result = response.text
    summary = response.headers
    summary['status'] = str(response.status_code)
    return summary, result


def isprimitive(body):
    """
    Given the body of a request will return a boolean to indicate if the
    value is a primitive value type.

    See:

    http://doc.fluidinfo.com/fluidDB/api/tag-values.html

    &

    http://bit.ly/hmrMzT

    For an explanation of the difference between primitive and opaque
    values.
    """
    bodyType = type(body)
    if bodyType in SERIALIZABLE_TYPES:
        if bodyType in ITERABLE_TYPES:
            if not all(isinstance(x, basestring) for x in body):
                return False
        return True
    else:
        return False


def build_url(path):
    """
    Given a path that is either a string or list of path elements, will return
    the correct URL
    """
    url = instance
    if isinstance(path, list):
        url += '/'
        url += '/'.join([urllib.quote(element, safe='') for element in path])
    else:
        url += urllib.quote(path)
    return url
