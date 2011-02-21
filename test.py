import fluidinfo
import uuid
import unittest

# Generic test user created on the Sandbox for the express purpose of
# running unit tests
USERNAME = 'test'
PASSWORD = 'test'

class TestFluidinfo(unittest.TestCase):
    """
    The names of the test methods are pretty self-explanatory. I've made sure
    to comment what's I'm testing if there are various test cases.
    """

    def setUp(self):
        # Only test against the SANDBOX
        fluidinfo.instance = fluidinfo.SANDBOX
        fluidinfo.logout()

    def test_login(self):
        # we're not logged in but able to do anonymous calls
        result = fluidinfo.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        new_namespace = str(uuid.uuid4())
        # and we can't do anything that requires us to be authenticated
        result = fluidinfo.call('POST', '/namespaces/test',
                             {'description': 'will fail',
                              'name': new_namespace})
        self.assertEqual('401', result[0]['status'])
        # Now lets log in with *bad* credentials
        fluidinfo.login(USERNAME, PASSWORD + 'bad_password')
        result = fluidinfo.call('GET', '/users/test')
        # Unauthorised due to bad credentials
        self.assertEqual('401', result[0]['status'])
        # Try again with the good case
        fluidinfo.login(USERNAME, PASSWORD)
        result = fluidinfo.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])

    def test_logout(self):
        # Lets first log in and check we're good to go
        fluidinfo.login(USERNAME, PASSWORD)
        result = fluidinfo.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        # Log out (this should clear the Authorization header)
        fluidinfo.logout()
        # We should still be able to do anonymous calls
        result = fluidinfo.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        # but we can't do anything that requires us to be authenticated
        new_namespace = str(uuid.uuid4())
        result = fluidinfo.call('POST', '/namespaces/test',
                             {'description': 'will fail',
                              'name': new_namespace})
        self.assertEqual('401', result[0]['status'])

    def test_isprimitive(self):
        """
        See:

        http://doc.fluidinfo.com/fluidDB/api/tag-values.html

        &

        http://doc.fluidinfo.com/fluidDB/api/http.html#payloads-containing-tag-values

        For explanation of primitive values.
        """
        # check the good case
        primitives = [1, 1.1, 'foo', u'foo', True, None, ['a', 'b', u'c']]
        for primitive in primitives:
            self.assertEqual(True, fluidinfo.isprimitive(primitive))
        # check a list containing something other than strings fails
        self.assertEqual(False, fluidinfo.isprimitive(['a', 1, 'b']))
        # check other types fail
        self.assertEqual(False, fluidinfo.isprimitive(dict()))

    # With the following tests we're ensuring that the arguments passed
    # into the call method are used correctly.

    def test_call_POST(self):
        fluidinfo.login(USERNAME, PASSWORD)
        new_namespace = str(uuid.uuid4())
        ns_body = {'description': 'a test namespace',
                   'name': new_namespace}
        # Make sure that if the body is a dict it gets translated to json
        result = fluidinfo.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        # Housekeeping
        fluidinfo.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_GET(self):
        fluidinfo.login(USERNAME, PASSWORD)
        # No query string args to append
        result = fluidinfo.call('GET', '/namespaces/test')
        self.assertEqual('200', result[0]['status'])
        # make sure the resulting json is turned into a Python dictionary
        self.assertTrue(isinstance(result[1], dict))
        # ...and we have the expected id
        self.assertTrue(result[1].has_key('id'))
        # The same call WITH query string args to append to the URL
        # eg we'll get /namespaces/test?returnDescription=True as the path
        result = fluidinfo.call('GET', '/namespaces/test', None, None,
                              returnDescription = True)
        self.assertEqual('200', result[0]['status'])
        # make sure the result has the expected description field
        self.assertTrue(result[1].has_key('description'))
        # finally we need to make sure that primitive values returned from
        # fluidDB are turned from their json representation to their
        # Pythonic form
        new_namespace = str(uuid.uuid4())
        new_tag = str(uuid.uuid4())
        ns_body = {'description': 'a test namespace',
                   'name': new_namespace}
        tag_body = {'description': 'a test tag', 'name': new_tag,
                    'indexed': False}
        # create a namespace and tag to use in a bit
        result = fluidinfo.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        ns_id = result[1]['id'] # for later use
        result = fluidinfo.call('POST', '/tags/test/' + new_namespace,
                              tag_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        path = '/'+'/'.join(['objects', ns_id, 'test', new_namespace,
                             new_tag])
        primitives = [1, 1.1, u'foo', ['a', 'b', u'c'], True, None, ]
        for primitive in primitives:
            result = fluidinfo.call('PUT', path, primitive)
            self.assertEqual('204', result[0]['status'])
            # GET the new tag value and check it gets translated back to
            # the correct type
            result = fluidinfo.call('GET', path)
            self.assertEqual('application/vnd.fluiddb.value+json',
                             result[0]['content-type'])
            self.assertTrue(isinstance(result[1], type(primitive)))
        # check the new /values GET works
        result = fluidinfo.call('GET', '/values', tags=['fluiddb/about',
            'test/%s/%s' % (new_namespace, new_tag)],
            query='has test/%s/%s' % (new_namespace, new_tag))
        self.assertEqual('200', result[0]['status'])
        self.assertTrue(result[1].has_key('results'))
        # Housekeeping
        fluidinfo.call('DELETE',
                     '/tags/test/' + new_namespace + '/' + new_tag)
        fluidinfo.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_HEAD(self):
        fluidinfo.login(USERNAME, PASSWORD)
        # Grab an object ID for a user for us to use in the HEAD path
        result = fluidinfo.call('GET', '/users/test')
        obj_id = result[1]['id']
        path = '/objects/%s/fluiddb/users/username' % obj_id
        result = fluidinfo.call('HEAD', path)
        self.assertEqual('200', result[0]['status'])
        self.assertFalse(result[1]) # no response body with HEAD call

    def test_call_PUT(self):
        fluidinfo.login(USERNAME, PASSWORD)
        new_namespace = str(uuid.uuid4())
        new_tag = str(uuid.uuid4())
        ns_body = {'description': 'a test namespace',
                   'name': new_namespace}
        tag_body = {'description': 'a test tag', 'name': new_tag,
                    'indexed': False}
        # create a namespace and tag to use in a bit
        result = fluidinfo.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        ns_id = result[1]['id'] # for later use
        result = fluidinfo.call('POST', '/tags/test/' + new_namespace,
                              tag_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        path = '/'+'/'.join(['objects', ns_id, 'test', new_namespace,
                             new_tag])
        # Make sure that primitive types are json encoded properly with
        # the correct mime-type, dicts are translated to json, the
        # mime-type argument for opaque types is used properly and if
        # no mime-type is supplied and the previous checks are not met
        # an appropriate exception is raised.
        primitives = [1, 1.1, 'foo', u'foo', True, None, ['a', 'b', u'c']]
        for primitive in primitives:
            result = fluidinfo.call('PUT', path, primitive)
            self.assertEqual('204', result[0]['status'])
            # call HEAD verb on that tag value to get the mime-type from
            # Fluidinfo
            result = fluidinfo.call('HEAD', path)
            self.assertEqual('application/vnd.fluiddb.value+json',
                             result[0]['content-type'])
        # dicts are json encoded
        result = fluidinfo.call('PUT', path, {'foo': 'bar'})
        # check again with HEAD verb
        result = fluidinfo.call('HEAD', path)
        self.assertEqual('application/json', result[0]['content-type'])
        # Make sure that the body and mime args work as expected (mime
        # overrides the primitive string type making the value opaque)
        result = fluidinfo.call('PUT', path, '<html><body><h1>Hello,'\
                              'World!</h1></body></html>', 'text/html')
        result = fluidinfo.call('HEAD', path)
        self.assertEqual('text/html', result[0]['content-type'])
        # unspecified mime-type on a non-primitive value results in an
        # exception
        self.assertRaises(TypeError, fluidinfo.call, 'PUT', path, object())
        # make sure it's possible to PUT a tag value using a list based path
        pathAsList = ['objects', ns_id, 'test', new_namespace, new_tag]
        result = fluidinfo.call('PUT', pathAsList, 'foo')
        self.assertEqual('204', result[0]['status'])
        # Housekeeping
        fluidinfo.call('DELETE',
                     '/tags/test/' + new_namespace + '/' + new_tag)
        fluidinfo.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_DELETE(self):
        fluidinfo.login(USERNAME, PASSWORD)
        # Simply create a new namespace and then delete it
        new_namespace = str(uuid.uuid4())
        body = {'description': 'a test namespace', 'name': new_namespace}
        result = fluidinfo.call('POST', '/namespaces/test', body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        result = fluidinfo.call('DELETE', '/namespaces/test/'+new_namespace)
        self.assertEqual('204', result[0]['status'])

    # The following test various behaviours of arguments passed into call that
    # don't depend upon the HTTP method being used.

    def test_custom_headers(self):
        custom_headers = {'Origin': 'http://foo.com'}
        result = fluidinfo.call('GET', '/users/test',
            custom_headers=custom_headers)
        self.assertEqual('200', result[0]['status'])
        self.assertEqual('http://foo.com',
            result[0]['access-control-allow-origin'])

    def test_build_url(self):
        # test with a list
        path = ['about', 'an/- object', 'test', 'foo']
        expected = fluidinfo.instance + '/about/an%2F-%20object/test/foo'
        actual = fluidinfo.build_url(path)
        self.assertEqual(expected, actual)
        # test with a string
        path = '/users/test'
        expected = fluidinfo.instance + '/users/test'
        actual = fluidinfo.build_url(path)
        self.assertEqual(expected, actual)
        # test with unicode (umlauts ftw)
        path = '/users/C\xfc\xe4h'
        expected = fluidinfo.instance + '/users/C%FC%E4h'
        actual = fluidinfo.build_url(path)
        self.assertEqual(expected, actual)

    def test_put_about_type_header(self):
        """
        There was a bug where the fluidinfo.py wasn't creating the correct
        content-type header when PUTting to an about tag value, this test
        re-creates it.
        """
        # ensures we have an object about foo
        headers, response = fluidinfo.call('GET', '/about/foo')
        # create a one off tag to use for the purposes of testing
        fluidinfo.login(USERNAME, PASSWORD)
        new_tag = str(uuid.uuid4())
        tag_body = {'description': 'a test tag', 'name': new_tag,
                    'indexed': False}
        # create a tag to use in a bit
        result = fluidinfo.call('POST', '/tags/test', tag_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        # make sure we can PUT using the about API
        try:
            header, content = fluidinfo.call('PUT', '/about/foo/test/'+new_tag,
                'this is a test')
            # check that it worked
            self.assertEqual('204', header['status'])
        finally:
            # Housekeeping
            fluidinfo.call('DELETE', '/tags/test/' + new_tag)


if __name__ == '__main__':
    unittest.main()
