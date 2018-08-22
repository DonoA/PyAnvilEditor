import struct, sys

def write_string(stream, string):
    stream.write(len(string).to_bytes(2, byteorder='big', signed=False))
    for c in string:
        stream.write(ord(c).to_bytes(1, byteorder='big', signed=False))

def register_parser(id, clazz):
    global _parsers

    _parsers[id] = clazz

def create_simple_nbt_class(tag_id, tag_name, tag_width, tag_parser):

    class DataNBTTag:

        clazz_width = tag_width
        clazz_name = tag_name
        clazz_parser = tag_parser
        clazz_id = tag_id

        @classmethod
        def parse(cls, stream, name):
            return cls(
                name, 
                struct.unpack(
                    cls.clazz_parser, 
                    stream.read(cls.clazz_width)
                )[0]
            )

        def __init__(self, tag_name, tag_value):
            self.tag_name = tag_name
            self.tag_value = tag_value

        def print(self, indent=''):
            print(indent + type(self).clazz_name + ': ' + self.tag_name + ' = ' + str(self.tag_value))

        def get(self):
            return self.tag_value

        def name(self):
            return self.tag_name

        def serialize(self, stream, include_name=True):
            if include_name:
                stream.write(type(self).clazz_id.to_bytes(1, byteorder='big', signed=False))
                write_string(stream, self.tag_name)

            stream.write(struct.pack(type(self).clazz_parser, self.tag_value))

    register_parser(tag_id, DataNBTTag)

    return DataNBTTag

def create_string_nbt_class(tag_id):
    class DataNBTTag:

        clazz_id = tag_id

        @classmethod
        def parse(cls, stream, name):
            payload_length = int.from_bytes(stream.read(2), byteorder='big', signed=False)
            payload = stream.read(payload_length).decode('utf-8')
            return cls(name, payload)

        def __init__(self, tag_name, tag_value):
            self.tag_name = tag_name
            self.tag_value = tag_value

        def print(self, indent=''):
            print(indent + 'String: ' + self.tag_name + ' = ' + str(self.tag_value))

        def get(self):
            return self.tag_value

        def name(self):
            return self.tag_name

        def serialize(self, stream, include_name=True):
            if include_name:
                stream.write(type(self).clazz_id.to_bytes(1, byteorder='big', signed=False))
                write_string(stream, self.tag_name)
            
            stream.write(len(self.tag_value).to_bytes(2, byteorder='big',signed=False))
            for c in self.tag_value:
                stream.write(ord(c).to_bytes(1, byteorder='big', signed=False))

    register_parser(tag_id, DataNBTTag)

    return DataNBTTag

def create_array_nbt_class(tag_id, tag_name, sub_type):
    class ArrayNBTTag:

        clazz_sub_type = sub_type
        clazz_name = tag_name
        clazz_id = tag_id

        @classmethod
        def parse(cls, stream, name):
            payload_length = int.from_bytes(stream.read(4), byteorder='big', signed=True)
            tag = cls(name)
            for i in range(payload_length):
                tag.add_child(cls.clazz_sub_type.parse(stream, 'None'))
            return tag

        def __init__(self, tag_name, children=[]):
            self.tag_name = tag_name
            self.children = children[:]
        
        def add_child(self, tag):
            self.children.append(tag)

        def name(self):
            return self.tag_name

        def print(self, indent=''):
            print(indent + type(self).clazz_name + ': ' + self.tag_name + ' size ' + str(len(self.children)))
            for c in self.children:
                c.print(indent + '  ')

        def serialize(self, stream, include_name=True):
            if include_name:
                stream.write(type(self).clazz_id.to_bytes(1, byteorder='big', signed=False))
                write_string(stream, self.tag_name)
                
            stream.write(len(self.children).to_bytes(4, byteorder='big', signed=True))

            for tag in self.children:
                tag.serialize(stream, include_name=False)

    register_parser(tag_id, ArrayNBTTag)

    return ArrayNBTTag

def create_list_nbt_class(tag_id):
    class ListNBTTag:

        clazz_id = tag_id

        @classmethod
        def parse(cls, stream, name):
            global _parsers

            sub_type = int.from_bytes(stream.read(1), byteorder='big', signed=False)
            payload_length = int.from_bytes(stream.read(4), byteorder='big', signed=True)
            tag = cls(name, sub_type)
            for i in range(payload_length):
                tag.add_child(_parsers[sub_type].parse(stream, 'None'))
            return tag

        def __init__(self, tag_name, sub_type_id, children=[]):
            self.tag_name = tag_name
            self.sub_type_id = sub_type_id
            self.children = children[:]
        
        def add_child(self, tag):
            self.children.append(tag)

        def name(self):
            return self.tag_name

        def print(self, indent=''):
            print(indent + 'List: ' + self.tag_name + ' size ' + str(len(self.children)))
            for c in self.children:
                c.print(indent + '  ')
        
        def serialize(self, stream, include_name=True):
            if include_name:
                stream.write(type(self).clazz_id.to_bytes(1, byteorder='big', signed=False))
                write_string(stream, self.tag_name)
            
            stream.write(self.sub_type_id.to_bytes(1, byteorder='big', signed=False))
            stream.write(len(self.children).to_bytes(4, byteorder='big', signed=True))

            for tag in self.children:
                tag.serialize(stream, include_name=False)

    register_parser(tag_id, ListNBTTag)

    return ListNBTTag

def create_compund_nbt_class(tag_id):
    class CompundNBTTag:

        clazz_id = tag_id

        @classmethod
        def parse(cls, stream, name):
            tag = cls(name)
            while stream.peek() != 0: # end tag
                tag.add_child(parse_nbt(stream))
            stream.read(1) # get rid of the end tag
            return tag

        def __init__(self, tag_name, children=[]):
            self.tag_name = tag_name
            self.children = { c.tag_name: c for c in children[:] }
        
        def add_child(self, tag):
            self.children[tag.tag_name] = tag

        def get(self, name):
            return self.children[name]

        def name(self):
            return self.tag_name

        def has(self, name):
            return name in self.children

        def to_dict(self):
            nd = {}
            for p in self.children:
                nd[p] = self.children[p].get()
            return nd

        def print(self, indent=''):
            print(indent + 'Compound: ' + self.tag_name + ' size ' + str(len(self.children)))
            for c in self.children:
                self.children[c].print(indent + '  ')

        def serialize(self, stream, include_name=True):
            if include_name:
                stream.write(type(self).clazz_id.to_bytes(1, byteorder='big', signed=False))
                write_string(stream, self.tag_name)
            
            for tag_name in self.children:
                self.children[tag_name].serialize(stream, include_name=True)
            
            stream.write((0).to_bytes(1, byteorder='big', signed=False))

    register_parser(tag_id, CompundNBTTag)

    return CompundNBTTag

_parsers = {}

ByteTag = create_simple_nbt_class(1, 'Byte', 1, '>b')
ShortTag = create_simple_nbt_class(2, 'Short', 2, '>h')
IntTag = create_simple_nbt_class(3, 'Int', 4, '>i')
LongTag = create_simple_nbt_class(4, 'Long', 8, '>q')
FloatTag = create_simple_nbt_class(5, 'Float', 4, '>f')
DoubleTag = create_simple_nbt_class(6, 'Double', 8, '>d')

ByteArrayTag = create_array_nbt_class(7, 'ByteArray', ByteTag)

StringTag = create_string_nbt_class(8)
ListTag = create_list_nbt_class(9)
CompoundTag = create_compund_nbt_class(10)

IntArrayTag = create_array_nbt_class(11, 'IntArray', IntTag)
LongArrayTag = create_array_nbt_class(12, 'LongArray', LongTag)

def parse_nbt(stream):
    global _parsers

    tag_type = int.from_bytes(stream.read(1), byteorder='big', signed=False)
    tag_name_length = int.from_bytes(stream.read(2), byteorder='big', signed=False)
    tag_name = stream.read(tag_name_length).decode('utf-8')

    return _parsers[tag_type].parse(stream, tag_name)

