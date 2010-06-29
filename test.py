import fluiddb
import uuid
import unittest

# Generic test user created on the Sandbox for the express purpose of
# running unit tests
USERNAME = 'test'
PASSWORD = 'test'

class TestFluidDB(unittest.TestCase):

    def setUp(self):
        # Only test against the SANDBOX
        fluiddb.instance = fluiddb.SANDBOX
        fluiddb.logout()

    def test_login(self):
        # we're not logged in but able to do anonymous calls
        result = fluiddb.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        new_namespace = str(uuid.uuid4())
        # and we can't do anything that requires us to be authenticated
        result = fluiddb.call('POST', '/namespaces/test',
                             {'description': 'will fail',
                              'name': new_namespace})
        self.assertEqual('401', result[0]['status'])
        # Now lets log in with *bad* credentials
        fluiddb.login(USERNAME, PASSWORD + 'bad_password')
        result = fluiddb.call('GET', '/users/test')
        # Unauthorised due to bad credentials
        self.assertEqual('401', result[0]['status'])
        # Try again with the good case
        fluiddb.login(USERNAME, PASSWORD)
        result = fluiddb.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])

    def test_logout(self):
        # Lets first log in and check we're good to go
        fluiddb.login(USERNAME, PASSWORD)
        result = fluiddb.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        # Log out (this should clear the Authorization header)
        fluiddb.logout()
        # We should still e able to do anonymous calls
        result = fluiddb.call('GET', '/users/test')
        self.assertEqual('200', result[0]['status'])
        # but we can't do anything that requires us to be authenticated
        new_namespace = str(uuid.uuid4())
        result = fluiddb.call('POST', '/namespaces/test',
                             {'description': 'will fail',
                              'name': new_namespace})
        self.assertEqual('401', result[0]['status'])

    def test_isprimitive(self):
        """
        See:
        http://doc.fluidinfo.com/fluidDB/api/tag-values.html
        &
        http://doc.fluidinfo.com/fluidDB/api/http.html#payloads-containing-tag-values
        For explanation of primitive values
        """
        # check the good case
        primitives = [1, 1.1, 'foo', u'foo', True, None, ['a', 'b', u'c']]
        for primitive in primitives:
            self.assertEqual(True, fluiddb.isprimitive(primitive))
        # check a list containing something other than strings fails
        self.assertEqual(False, fluiddb.isprimitive(['a', 1, 'b']))
        # check other types fail
        self.assertEqual(False, fluiddb.isprimitive(dict()))

    # With the following tests we're ensuring that the arguments passed
    # into the call method are used correctly.

    def test_call_POST(self):
        fluiddb.login(USERNAME, PASSWORD)
        new_namespace = str(uuid.uuid4())
        ns_body = {'description': 'a test namespace',
                   'name': new_namespace}
        # Make sure that if the body is a dict it gets translated to json
        result = fluiddb.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        # Housekeeping
        fluiddb.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_GET(self):
        fluiddb.login(USERNAME, PASSWORD)
        # No query string args to append
        result = fluiddb.call('GET', '/namespaces/test')
        self.assertEqual('200', result[0]['status'])
        # make sure the resulting json is turned into a Python dictionary
        self.assertTrue(isinstance(result[1], dict))
        # ...and we have the expected id
        self.assertTrue(result[1].has_key('id'))
        # The same call WITH query string args to append to the URL
        # eg we'll get /namespaces/test?returnDescription=True as the path
        result = fluiddb.call('GET', '/namespaces/test', None, None,
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
        result = fluiddb.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        ns_id = result[1]['id'] # for later use
        result = fluiddb.call('POST', '/tags/test/' + new_namespace,
                              tag_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        path = '/'+'/'.join(['objects', ns_id, 'test', new_namespace,
                             new_tag])
        primitives = [1, 1.1, u'foo', True, None, ['a', 'b', u'c']]
        for primitive in primitives:
            result = fluiddb.call('PUT', path, primitive)
            self.assertEqual('204', result[0]['status'])
            # GET the new tag value and check it gets translated back to
            # the correct type
            result = fluiddb.call('GET', path)
            self.assertEqual('application/vnd.fluiddb.value+json',
                             result[0]['content-type'])
            self.assertTrue(isinstance(result[1], type(primitive)))
        # Housekeeping
        fluiddb.call('DELETE',
                     '/tags/test/' + new_namespace + '/' + new_tag)
        fluiddb.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_HEAD(self):
        fluiddb.login(USERNAME, PASSWORD)
        # Grab an object ID for a user for us to use in the HEAD path
        result = fluiddb.call('GET', '/users/test')
        obj_id = result[1]['id']
        path = '/objects/%s/fluiddb/users/username' % obj_id
        result = fluiddb.call('HEAD', path)
        self.assertEqual('200', result[0]['status'])
        self.assertFalse(result[1]) # no response body with HEAD call

    def test_call_PUT(self):
        fluiddb.login(USERNAME, PASSWORD)
        new_namespace = str(uuid.uuid4())
        new_tag = str(uuid.uuid4())
        ns_body = {'description': 'a test namespace',
                   'name': new_namespace}
        tag_body = {'description': 'a test tag', 'name': new_tag,
                    'indexed': False}
        # create a namespace and tag to use in a bit
        result = fluiddb.call('POST', '/namespaces/test', ns_body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        ns_id = result[1]['id'] # for later use
        result = fluiddb.call('POST', '/tags/test/' + new_namespace,
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
            result = fluiddb.call('PUT', path, primitive)
            self.assertEqual('204', result[0]['status'])
            # call HEAD verb on that tag value to get the mime-type from 
            # FluidDB
            result = fluiddb.call('HEAD', path)
            self.assertEqual('application/vnd.fluiddb.value+json',
                             result[0]['content-type'])
        # dicts are json encoded
        result = fluiddb.call('PUT', path, {'foo': 'bar'})
        # check again with HEAD verb
        result = fluiddb.call('HEAD', path)
        self.assertEqual('application/json', result[0]['content-type'])
        # Make sure that the body and mime args work as expected (mime
        # overrides the primitive string type making the value opaque)
        result = fluiddb.call('PUT', path, '<html><body><h1>Hello,'\
                              'World!</h1></body></html>', 'text/html')
        result = fluiddb.call('HEAD', path)
        self.assertEqual('text/html', result[0]['content-type'])
        # unspecified mime-type on a non-primitive value results in an 
        # exception
        self.assertRaises(TypeError, fluiddb.call, 'PUT', path, object())
        # Housekeeping
        fluiddb.call('DELETE',
                     '/tags/test/' + new_namespace + '/' + new_tag)
        fluiddb.call('DELETE', '/namespaces/test/'+new_namespace)

    def test_call_DELETE(self):
        fluiddb.login(USERNAME, PASSWORD)
        # Simply create a new namespace and then delete it
        new_namespace = str(uuid.uuid4())
        body = {'description': 'a test namespace', 'name': new_namespace}
        result = fluiddb.call('POST', '/namespaces/test', body)
        self.assertEqual('201', result[0]['status'])
        self.assertTrue(result[1].has_key('id'))
        result = fluiddb.call('DELETE', '/namespaces/test/'+new_namespace)
        self.assertEqual('204', result[0]['status'])

if __name__ == '__main__':
    unittest.main()
