from pyanvil.stream import InputStream, OutputStream

class TestInputStream:

    def test_reading_data(args):
        stream = InputStream(b'Hello World')
        read_hello = stream.read(5)
        stream.read(1)
        read_world = stream.read(5)
        assert read_hello == b'Hello'
        assert read_world == b'World'

    def test_peeking_data(args):
        stream = InputStream(b'Hello World')
        read_hello = stream.read(5)
        peek_space = stream.peek()
        assert read_hello == b'Hello'
        assert peek_space == 32

class TestOutputStream:

    def test_writing_data(args):
        stream = OutputStream()
        stream.write(b'Hello World')
        stream_data = stream.get_data()
        assert stream_data == b'Hello World'