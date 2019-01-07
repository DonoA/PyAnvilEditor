from pyanvil.nbt import ByteTag, ShortTag, IntTag, LongTag, FloatTag, DoubleTag
from pyanvil.nbt import ByteArrayTag, StringTag, ListTag, CompoundTag, IntArrayTag, LongArrayTag
from pyanvil.nbt import parse_nbt
from pyanvil.stream import OutputStream, InputStream

def build_simple_nbt_tag_test(clz, test_val, test_bin):
    class TestSimpleNBTTag:
        def test_serializing_with_name(args):
            tag = clz(test_val, tag_name='Test')
            stream = OutputStream()
            tag.serialize(stream, include_name=True)
            binary_tag = list(stream.get_data())
            expected_tag = [clz.clazz_id, 0, 4] + \
                list(b'Test') + \
                test_bin
            assert binary_tag == expected_tag, f'Tag {clz.clazz_name}'

        def test_serializing_without_name(args):
            tag = clz(test_val, tag_name='Test')
            stream = OutputStream()
            tag.serialize(stream, include_name=False)
            binary_tag = list(stream.get_data())
            expected_tag = test_bin
            assert binary_tag == expected_tag, f'Tag {clz.clazz_name}'

        def test_deserializing(args):
            raw_tag = InputStream(bytearray([clz.clazz_id, 0, 4] + \
                list(b'Test') + \
                test_bin))
            parsed_tag = parse_nbt(raw_tag)
            expected_tag = clz(test_val, tag_name='Test')
            assert parsed_tag == expected_tag, f'Tag {clz.clazz_name}'

    return TestSimpleNBTTag

def build_array_nbt_tag_test(clz, test_vals, test_bins):
    class TestArrayNBTTag:
        def test_serializing(args):
            tag = clz('Test', children=[
                clz.clazz_sub_type(v) for v in test_vals
            ])
            stream = OutputStream()
            tag.serialize(stream, include_name=True)
            binary_tag = list(stream.get_data())
            expected_tag = [clz.clazz_id, 0, 4] + \
                list(b'Test') + \
                [0,0,0,len(test_vals)] +\
                [b for sublist in test_bins for b in sublist]
            assert binary_tag == expected_tag, f'Tag {clz.clazz_name}'

        def test_deserializing(args):
            raw_tag = InputStream(bytearray([clz.clazz_id, 0, 4] + \
                list(b'Test') + \
                [0,0,0,len(test_vals)] +\
                [b for sublist in test_bins for b in sublist]))
            parsed_tag = parse_nbt(raw_tag)
            expected_tag = clz('Test', children=[
                clz.clazz_sub_type(v) for v in test_vals
            ])
            assert parsed_tag == expected_tag, f'Tag {clz.clazz_name}'

    return TestArrayNBTTag
        

TestByteTag = build_simple_nbt_tag_test(ByteTag, 75, [75])
TestShortTag = build_simple_nbt_tag_test(ShortTag, 3*10**4, [117, 48])
TestIntTag = build_simple_nbt_tag_test(IntTag, 2*10**9, [119, 53, 148, 0])
TestLongTag = build_simple_nbt_tag_test(LongTag, 5*10**12, [0, 0, 4, 140, 39, 57, 80, 0])
TestFloatTag = build_simple_nbt_tag_test(FloatTag, 1.5, [63, 192, 0, 0])
TestDoubleTag = build_simple_nbt_tag_test(DoubleTag, 125.135, [64, 95, 72, 163, 215, 10, 61, 113])

TestByteArrayTag = build_array_nbt_tag_test(ByteArrayTag, [75, 25], [[75], [25]])
TestIntArrayTag = build_array_nbt_tag_test(IntArrayTag, [3*10**4, 2*10**9], [[0, 0, 117, 48], [119, 53, 148, 0]])
TestLongArrayTag = build_array_nbt_tag_test(LongArrayTag, [2*10**9, 5*10**12], [[0, 0, 0, 0, 119, 53, 148, 0],[0, 0, 4, 140, 39, 57, 80, 0]])

class TestStringTag:
    def test_serializing(args):
        tag = StringTag('Hello World', tag_name='Test')
        stream = OutputStream()
        tag.serialize(stream, include_name=True)
        binary_tag = list(stream.get_data())
        expected_tag = [8, 0, 4] + \
            list(b'Test') + \
            [0,len('Hello World')] +\
            list(b'Hello World')
        assert binary_tag == expected_tag, 'Tag StringTag'

    def test_deserializing(args):
        raw_tag = InputStream(bytearray([8, 0, 4] + \
            list(b'Test') + \
            [0,len('Hello World')] +\
            list(b'Hello World')))
        parsed_tag = parse_nbt(raw_tag)
        tag = StringTag('Hello World', tag_name='Test')
        assert parsed_tag == tag, 'Tag StringTag'

class TestListNBTTag:
    def test_serializing_simple_data(args):
        tag = ListTag(FloatTag.clazz_id, tag_name='Test', children=[
            FloatTag(1.5),
            FloatTag(11.15)
        ])
        stream = OutputStream()
        tag.serialize(stream, include_name=True)
        binary_tag = list(stream.get_data())
        expected_tag = [9, 0, 4] + \
            list(b'Test') + \
            [5, 0, 0, 0, 2] +\
            [63, 192, 0, 0, 65, 50, 102, 102]
            
        assert binary_tag == expected_tag, 'Tag ListTag with FloatTag elements'

    def test_deserializing_simple_data(args):
        raw_tag = InputStream(bytearray([9, 0, 4] + \
            list(b'Test') + \
            [5, 0, 0, 0, 2] +\
            [63, 192, 0, 0, 65, 50, 102, 102]))
        parsed_tag = parse_nbt(raw_tag)
        tag = ListTag(FloatTag.clazz_id, tag_name='Test', children=[
            FloatTag(1.5),
            FloatTag(11.149999618530273) # float pack error
        ])
        assert parsed_tag == tag, 'Tag ListTag with FloatTag elements'

    def test_serializing_list_data(args):
        tag = ListTag(ListTag.clazz_id, tag_name='Test', children=[
            ListTag(ByteTag.clazz_id, children=[ByteTag(25), ByteTag(31)]),
            ListTag(FloatTag.clazz_id, children=[FloatTag(1.5)])
        ])
        stream = OutputStream()
        tag.serialize(stream, include_name=True)
        binary_tag = list(stream.get_data())

        expected_tag = [9, 0, 4] + \
            list(b'Test') + \
            [9, 0, 0, 0, 2] +\
            [1, 0, 0, 0, 2] +\
            [25, 31] +\
            [5, 0, 0, 0, 1] +\
            [63, 192, 0, 0]
            
        assert binary_tag == expected_tag, 'Tag ListTag with ListTag elements'

    def test_deserializing_list_data(args):
        raw_tag = InputStream(bytearray([9, 0, 4] + \
            list(b'Test') + \
            [9, 0, 0, 0, 2] +\
            [1, 0, 0, 0, 2] +\
            [25, 31] +\
            [5, 0, 0, 0, 1] +\
            [63, 192, 0, 0]))
        parsed_tag = parse_nbt(raw_tag)
        tag = ListTag(ListTag.clazz_id, tag_name='Test', children=[
            ListTag(ByteTag.clazz_id, children=[ByteTag(25), ByteTag(31)]),
            ListTag(FloatTag.clazz_id, children=[FloatTag(1.5)])
        ])
        assert parsed_tag == tag, 'Tag ListTag with ListTag elements'

    def test_serializing_compund_data(args):
        tag = ListTag(CompoundTag.clazz_id, tag_name='Test', children=[
            CompoundTag(children=[ByteTag(25, tag_name='dp1'), ByteTag(31, tag_name='dp2')]),
            CompoundTag(children=[ByteTag(25, tag_name='dp3'), ByteTag(31, tag_name='dp4')])
        ])
        stream = OutputStream()
        tag.serialize(stream, include_name=True)
        binary_tag = list(stream.get_data())
        expected_tag = [9, 0, 4] + \
            list(b'Test') + \
            [10, 0, 0, 0, 2] +\
            [1, 0, 3,] + list(b'dp1') + [25] +\
            [1, 0, 3,] + list(b'dp2') + [31, 0] +\
            [1, 0, 3,] + list(b'dp3') + [25] +\
            [1, 0, 3,] + list(b'dp4') + [31, 0]
            
        assert binary_tag == expected_tag, 'Tag ListTag with ListTag elements'

    def test_deserializing_compund_data(args):
        raw_tag = InputStream(bytearray([9, 0, 4] + \
            list(b'Test') + \
            [10, 0, 0, 0, 2] +\
            [1, 0, 3,] + list(b'dp1') + [25] +\
            [1, 0, 3,] + list(b'dp2') + [31, 0] +\
            [1, 0, 3,] + list(b'dp3') + [25] +\
            [1, 0, 3,] + list(b'dp4') + [31, 0]))
        parsed_tag = parse_nbt(raw_tag)
        tag = ListTag(CompoundTag.clazz_id, tag_name='Test', children=[
            CompoundTag(children=[ByteTag(25, tag_name='dp1'), ByteTag(31, tag_name='dp2')]),
            CompoundTag(children=[ByteTag(25, tag_name='dp3'), ByteTag(31, tag_name='dp4')])
        ])
        assert parsed_tag == tag, 'Tag ListTag with ListTag elements'

class TestCompoundNBTTag:
    def test_serializing(args):
        tag = CompoundTag(tag_name='Test', children=[
            ByteTag(25, tag_name='dp1'), 
            FloatTag(1.5, tag_name='dp2'),
            ListTag(ByteTag.clazz_id, tag_name='dp3', children=[
                ByteTag(35)
            ]),
            CompoundTag(tag_name='dp4', children=[
                ByteArrayTag(tag_name='sub_dp', children=[
                    ByteTag(10),
                    ByteTag(20) 
                ])
            ])
        ])
        stream = OutputStream()
        tag.serialize(stream, include_name=True)
        binary_tag = list(stream.get_data())
        expected_tag = [10, 0, 4] + \
            list(b'Test') + \
            [1, 0, 3,] + list(b'dp1') + [25] +\
            [5, 0, 3,] + list(b'dp2') + [63, 192, 0, 0] +\
            [9, 0, 3,] + list(b'dp3') + [1, 0, 0, 0, 1] + [35] +\
            [10, 0, 3,] + list(b'dp4') +\
            [7, 0, 6,] + list(b'sub_dp') + [0, 0, 0, 2, 10, 20] + [0] +\
            [0]
        assert binary_tag == expected_tag, 'Tag ListTag with ListTag elements'

    def test_deserializing(args):
        raw_tag = InputStream(bytearray([10, 0, 4] + \
            list(b'Test') + \
            [1, 0, 3,] + list(b'dp1') + [25] +\
            [5, 0, 3,] + list(b'dp2') + [63, 192, 0, 0] +\
            [9, 0, 3,] + list(b'dp3') + [1, 0, 0, 0, 1] + [35] +\
            [10, 0, 3,] + list(b'dp4') +\
            [7, 0, 6,] + list(b'sub_dp') + [0, 0, 0, 2, 10, 20] + [0] +\
            [0]))
        parsed_tag = parse_nbt(raw_tag)
        tag = CompoundTag(tag_name='Test', children=[
            ByteTag(25, tag_name='dp1'), 
            FloatTag(1.5, tag_name='dp2'),
            ListTag(ByteTag.clazz_id, tag_name='dp3', children=[
                ByteTag(35)
            ]),
            CompoundTag(tag_name='dp4', children=[
                ByteArrayTag(tag_name='sub_dp', children=[
                    ByteTag(10),
                    ByteTag(20) 
                ])
            ])
        ])
        assert parsed_tag == tag, 'Tag ListTag with ListTag elements'
