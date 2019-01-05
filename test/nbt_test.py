from pyanvil.nbt import ByteTag, ShortTag, IntTag, LongTag, FloatTag, DoubleTag
from pyanvil.nbt import ByteArrayTag, StringTag, ListTag, CompoundTag, IntArrayTag, LongArrayTag
from pyanvil.nbt import parse_nbt
from pyanvil.stream import OutputStream, InputStream

def build_simple_nbt_tag_test(clz, tag_id, test_val, test_bin):
    class TestSimpleNBTTag:
        def test_serializing_with_name(args):
            tag = clz('Test', test_val)
            stream = OutputStream()
            tag.serialize(stream, include_name=True)
            binary_tag = list(stream.get_data())
            expected_tag = [tag_id, 0x0, 0x4] + \
                list(b'Test') + \
                test_bin
            assert binary_tag == expected_tag, f'Tag {clz.clazz_name}'

        def test_serializing_without_name(args):
            tag = clz('Test', test_val)
            stream = OutputStream()
            tag.serialize(stream, include_name=False)
            binary_tag = list(stream.get_data())
            expected_tag = test_bin
            assert binary_tag == expected_tag, f'Tag {clz.clazz_name}'

        def test_deserializing(args):
            raw_tag = InputStream(bytearray([tag_id, 0x0, 0x4] + \
                list(b'Test') + \
                test_bin))
            parsed_tag = parse_nbt(raw_tag)
            expected_tag = clz('Test', test_val)
            assert parsed_tag == expected_tag, f'Tag {clz.clazz_name}'

    return TestSimpleNBTTag

TestByteTag = build_simple_nbt_tag_test(ByteTag, 0x1, 75, [75])
TestShortTag = build_simple_nbt_tag_test(ShortTag, 0x2, 3*10**4, [117, 48])
TestIntTag = build_simple_nbt_tag_test(IntTag, 0x3, 2*10**9, [119, 53, 148, 0])
TestLongTag = build_simple_nbt_tag_test(LongTag, 0x4, 5*10**12, [0, 0, 4, 140, 39, 57, 80, 0])
TestFloat = build_simple_nbt_tag_test(FloatTag, 0x5, 1.5, [63, 192, 0, 0])
TestDouble = build_simple_nbt_tag_test(DoubleTag, 0x6, 125.135, [64, 95, 72, 163, 215, 10, 61, 113])


    