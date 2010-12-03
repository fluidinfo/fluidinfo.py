FluidDB.py
==========

About
-----

This is a very thin wrapper on top of the FluidDB RESTful API. FluidDB is an
openly writable platform for the web of things. More information about FluidDB
can be found here:

http://fluidinfo.com/

The RESTful API is described here:

http://api.fluidinfo.com/

Originally based upon work by Seo Sanghyeon found here:

http://bitbucket.org/sanxiyn/fluidfs

This module has been extracted, extended and unit-tests were added by Nicholas
Tollervey (http://ntoll.org)

Usage
-----

A quick example is a great introduction::

    $ python
    Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)
    [GCC 4.4.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import fluiddb
    >>> fluiddb.instance
    'https://fluiddb.fluidinfo.com'
    >>> fluiddb.login('username', 'password')
    >>> fluiddb.call('GET', '/users/test')
    ({'status': '200', 'content-length': '62',
    'content-location': 'https://fluiddb.fluidinfo.com/users/test',
    'server': 'nginx/0.7.65', 'connection': 'keep-alive',
    'cache-control': 'no-cache', 'date': 'Fri, 03 Dec 2010 17:07:34 GMT',
    'content-type': 'application/json'}, {u'name': u'test',
    u'id': u'8cc64c7d-a155-4246-ab2b-564f87fd9222'})

Simply import fluiddb to get started. The fluiddb.instance variable indicates to which instance of FluidDB the module is using (it defaults to the main instance). Please make use of the fluiddb.MAIN and fluiddb.SANDBOX "constants" to change instance::

    >>> fluiddb.SANDBOX
    'https://sandbox.fluidinfo.com'
    >>> fluiddb.instance = fluiddb.SANDBOX
    >>> fluiddb.MAIN
    'https://fluiddb.fluidinfo.com'
    >>> fluiddb.instance = fluiddb.MAIN

Use the login and logout functions to, er, login and logout (what did you expect..?)::

    >>> fluiddb.login('username', 'password')
    >>> fluiddb.logout()

The most important function provided by the fluiddb module is call(). You must supply at least the HTTP method and path as the first two arguments::

    >>> fluiddb.call('GET', '/users/test')
    ({'status': '200', 'content-length': '62',
    'content-location': 'https://fluiddb.fluidinfo.com/users/test',
    'server': 'nginx/0.7.65', 'connection': 'keep-alive',
    'cache-control': 'no-cache', 'date': 'Fri, 03 Dec 2010 17:07:34 GMT',
    'content-type': 'application/json'}, {u'name': u'test',
    u'id': u'8cc64c7d-a155-4246-ab2b-564f87fd9222'})

Notice how call() returns a tuple containing two items:

* The header dictionary
* The content of the response (if there is any)

Often it is simply better to do the following::

    >>> headers, content = fluiddb.call('GET', '/users/test')

It is also possible to send the path as a list of path elements::

    >>> headers, content = fluiddb.call('GET', ['about','yes/no','test','foo'])

Which will ensure that each element is correctly percent encoded even if it includes problem characters like slash: '/' (essential for being able to use the "about" based API.

If the API involves sending json data to FluidDB simply send the appropriate Python dict object and fluiddb.py will jsonify it appropriately for you::

    >>> headers, content = fluiddb.call('POST', '/objects', body={'about': 'an-example'})

If the body argument isn't a Python dictionary then you can only be PUTting a tag-value on an object. In which case, it's possible to set the mime-type of the value passed in body::

    >>> headers, content = fluiddb.call('PUT', '/about/an-example/test/foo', body='<html><body>Hello, World!</body></html>', mime='text/html')

Furthermore, if you want to send some custom headers to FluidDB (useful for testing purposes) then supply them as a dictionary via the custom_headers argument::

    >>> headers, content = fluiddb.call('GET', '/users/test', custom_headers={'Origin': 'http://foo.com'})

Finally, should you be sending a query via the /values endpoint then you can supply the list of tags whose values you want returned via the tags argument::

    >>> headers, content = fluiddb.call('GET', '/values', tags=['fluiddb/about', 'twitter.com/users/screen_name'], query='has ntoll/met')

Feedback welcome!
