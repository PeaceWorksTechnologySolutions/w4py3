"""Test modified functionality of FieldStorage."""

import unittest

from io import BytesIO

from WebUtils.FieldStorage import FieldStorage, hasSeparator


class TestFieldStorage(unittest.TestCase):

    def testGetRequest(self):
        fs = FieldStorage(environ={
            'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'a=1&b=2&b=3&c=3'})
        self.assertEqual(fs.getfirst('a'), '1')
        self.assertEqual(fs.getfirst('b'), '2')
        self.assertEqual(fs.getfirst('c'), '3')
        self.assertEqual(fs.getlist('a'), ['1'])
        self.assertEqual(fs.getlist('b'), ['2', '3'])
        self.assertEqual(fs.getlist('c'), ['3'])

    def testPostRequestWithQuery(self):
        fs = FieldStorage(fp=BytesIO(), environ={
            'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'a=1&b=2&b=3&c=3'})
        self.assertEqual(fs.getfirst('a'), '1')
        self.assertEqual(fs.getfirst('b'), '2')
        self.assertEqual(fs.getfirst('c'), '3')
        self.assertEqual(fs.getlist('a'), ['1'])
        self.assertEqual(fs.getlist('b'), ['2', '3'])
        self.assertEqual(fs.getlist('c'), ['3'])

    def testPostRequestWithBody(self):
        fs = FieldStorage(fp=BytesIO(b'd=4&e=5&e=6&f=6'), environ={
            'REQUEST_METHOD': 'POST'})
        self.assertEqual(fs.getfirst('d'), '4')
        self.assertEqual(fs.getfirst('e'), '5')
        self.assertEqual(fs.getfirst('f'), '6')
        self.assertEqual(fs.getlist('d'), ['4'])
        self.assertEqual(fs.getlist('e'), ['5', '6'])
        self.assertEqual(fs.getlist('f'), ['6'])

    def testPostRequestWithSpacesInValues(self):
        fs = FieldStorage(fp=BytesIO(), environ={
            'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'a=b%20c+d'})
        self.assertEqual(fs.getfirst('a'), 'b c d')
        fs = FieldStorage(fp=BytesIO(b'a=b%20c+d'), environ={
            'REQUEST_METHOD': 'POST'})
        self.assertEqual(fs.getfirst('a'), 'b c d')

    def testPostRequestOverrides(self):
        fs = FieldStorage(fp=BytesIO(b'b=8&c=9&d=4&e=5&e=6&f=6'), environ={
            'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'a=1&b=2&b=3&c=3'})
        self.assertEqual(fs.getfirst('a'), '1')
        self.assertEqual(fs.getfirst('b'), '8')
        self.assertEqual(fs.getfirst('c'), '9')
        self.assertEqual(fs.getfirst('d'), '4')
        self.assertEqual(fs.getfirst('e'), '5')
        self.assertEqual(fs.getfirst('f'), '6')
        self.assertEqual(fs.getlist('a'), ['1'])
        self.assertEqual(fs.getlist('b'), ['8'])
        self.assertEqual(fs.getlist('c'), ['9'])
        self.assertEqual(fs.getlist('d'), ['4'])
        self.assertEqual(fs.getlist('e'), ['5', '6'])
        self.assertEqual(fs.getlist('f'), ['6'])

    def testPostRequestWithTooManyFields(self):
        fs = FieldStorage(
            fp=BytesIO(),
            environ={'REQUEST_METHOD': 'POST',
                     'QUERY_STRING': 'a=1&a=2&a=3&a=4'},
            max_num_fields=4)
        self.assertEqual(fs.getlist('a'), ['1', '2', '3', '4'])
        if hasattr(fs, 'max_num_fields'):  # only test if this is supported
            self.assertRaises(
                ValueError, FieldStorage,
                fp=BytesIO(),
                environ={'REQUEST_METHOD': 'POST',
                         'QUERY_STRING': 'a=1&a=2&a=3&a=4'},
                max_num_fields=3)

    def testPostRequestWithQueryWithSemicolon1(self):
        fs = FieldStorage(fp=BytesIO(), environ={
            'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'a=1&b=2;b=3&c=3'})
        self.assertEqual(fs.getfirst('a'), '1')
        self.assertEqual(fs.getfirst('c'), '3')
        self.assertEqual(fs.getlist('a'), ['1'])
        self.assertEqual(fs.getlist('c'), ['3'])
        if hasSeparator():  # new Python version, splits only &
            self.assertEqual(fs.getfirst('b'), '2;b=3')
            self.assertEqual(fs.getlist('b'), ['2;b=3'])
            fs = FieldStorage(
                fp=BytesIO(),
                environ={'REQUEST_METHOD': 'POST',
                         'QUERY_STRING': 'a=1&b=2&b=3&c=3'},
                separator='&')
            self.assertEqual(fs.getfirst('a'), '1')
            self.assertEqual(fs.getfirst('b'), '2')
            self.assertEqual(fs.getfirst('c'), '3')
            self.assertEqual(fs.getlist('a'), ['1'])
            self.assertEqual(fs.getlist('b'), ['2', '3'])
            self.assertEqual(fs.getlist('c'), ['3'])
        else:  # old Python version, splits ; and &
            self.assertEqual(fs.getfirst('b'), '2')
            self.assertEqual(fs.getlist('b'), ['2', '3'])

    def testPostRequestWithQueryWithSemicolon2(self):
        fs = FieldStorage(fp=BytesIO(), environ={
            'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'a=1;b=2&b=3;c=3'})
        if hasSeparator():  # new Python version, splits only &
            self.assertEqual(fs.getfirst('a'), '1;b=2')
            self.assertEqual(fs.getfirst('b'), '3;c=3')
            self.assertIsNone(fs.getfirst('c'))
            self.assertEqual(fs.getlist('a'), ['1;b=2'])
            self.assertEqual(fs.getlist('b'), ['3;c=3'])
            self.assertEqual(fs.getlist('c'), [])
            fs = FieldStorage(
                fp=BytesIO(),
                environ={'REQUEST_METHOD': 'POST',
                         'QUERY_STRING': 'a=1;b=2;b=3;c=3'},
                separator=';')
            self.assertEqual(fs.getfirst('a'), '1')
            self.assertEqual(fs.getfirst('b'), '2')
            self.assertEqual(fs.getfirst('c'), '3')
            self.assertEqual(fs.getlist('a'), ['1'])
            self.assertEqual(fs.getlist('b'), ['2', '3'])
            self.assertEqual(fs.getlist('c'), ['3'])
        else:  # old Python version, splits ; and &
            self.assertEqual(fs.getfirst('a'), '1')
            self.assertEqual(fs.getfirst('b'), '2')
            self.assertEqual(fs.getfirst('c'), '3')
            self.assertEqual(fs.getlist('a'), ['1'])
            self.assertEqual(fs.getlist('b'), ['2', '3'])
            self.assertEqual(fs.getlist('c'), ['3'])

    def testPostRequestWithoutContentLength(self):
        # see https://github.com/python/cpython/issues/71964
        fs = FieldStorage(
            fp=BytesIO(b'{"test":123}'),
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': 'application/json'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/json'})
        self.assertEqual(fs.type, 'application/json')
        self.assertEqual(fs.length, -1)
        self.assertEqual(fs.bytes_read, 12)
        assert fs.file.read() == '{"test":123}'

    def testPostRequestWithContentLengthAndContentDispositionInline(self):
        # see https://github.com/python/cpython/issues/71964
        fs = FieldStorage(
            fp=BytesIO(b'{"test":123}'),
            headers={'content-length': 12, 'content-disposition': 'inline',
                     'content-type': 'application/json'},
            environ={'REQUEST_METHOD': 'POST'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/json', 'content-length': 12,
            'content-disposition': 'inline'})
        self.assertEqual(fs.disposition, 'inline')
        self.assertIsNone(fs.filename)
        self.assertEqual(fs.type, 'application/json')
        self.assertEqual(fs.length, 12)
        self.assertEqual(fs.bytes_read, 12)
        self.assertEqual(fs.file.read(), '{"test":123}')

    def testPostRequestWithContentLengthAndContentDispositionAttachment(self):
        # not affected by https://github.com/python/cpython/issues/71964
        fs = FieldStorage(
            fp=BytesIO(b'{"test":123}'),
            headers={'content-length': 12,
                     'content-disposition': 'attachment; filename="foo.json"',
                     'content-type': 'application/json'},
            environ={'REQUEST_METHOD': 'POST'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/json', 'content-length': 12,
            'content-disposition': 'attachment; filename="foo.json"'})
        self.assertEqual(fs.disposition, 'attachment')
        self.assertEqual(fs.filename, 'foo.json')
        self.assertEqual(fs.type, 'application/json')
        self.assertEqual(fs.length, 12)
        self.assertEqual(fs.bytes_read, 12)
        self.assertEqual(fs.file.read(), b'{"test":123}')

    def testPostRequestWithContentLengthButWithoutContentDisposition(self):
        # see https://github.com/python/cpython/issues/71964
        fs = FieldStorage(fp=BytesIO(b'{"test":123}'), environ={
            'CONTENT_LENGTH': 12, 'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/json'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/json', 'content-length': 12})
        self.assertEqual(fs.disposition, '')
        self.assertEqual(fs.type, 'application/json')
        self.assertEqual(fs.length, 12)
        self.assertEqual(fs.bytes_read, 12)
        self.assertEqual(fs.file.read(), '{"test":123}')

    def testPostRequestWithUtf8BinaryData(self):
        text = 'The \u2603 by Raymond Briggs'
        content = text.encode('utf-8')
        length = len(content)
        fs = FieldStorage(fp=BytesIO(content), environ={
            'CONTENT_LENGTH': length, 'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/octet-stream'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/octet-stream',
            'content-length': length})
        self.assertEqual(fs.type, 'application/octet-stream')
        self.assertEqual(fs.length, length)
        self.assertEqual(fs.bytes_read, length)
        self.assertEqual(fs.file.read(), text)

    def testPostRequestWithNonUtf8BinaryData(self):
        # see https://github.com/WebwareForPython/w4py3/issues/14
        content = b'\xfe\xff\xc0'
        with self.assertRaises(UnicodeDecodeError):
            content.decode('utf-8')
        length = len(content)
        fs = FieldStorage(fp=BytesIO(content), environ={
            'CONTENT_LENGTH': length, 'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/octet-stream'})
        self.assertEqual(fs.headers, {
            'content-type': 'application/octet-stream',
            'content-length': length})
        self.assertEqual(fs.type, 'application/octet-stream')
        self.assertEqual(fs.length, length)
        self.assertEqual(fs.bytes_read, length)
        self.assertEqual(fs.file.read(), content)
