import struct, sys

class _DataParser:
    def __init__(self, tag_name, tag_length, tag_parser):
        self.tag_name = tag_name
        self.tag_length = tag_length
        self.tag_parser = tag_parser

    def parse(self, stream, name):
        return DataNBTTag(
            self.tag_name, 
            name, 
            struct.unpack(
                self.tag_parser, 
                stream.read(self.tag_length)
            )[0]
        )

class _ArrayParser:
    def __init__(self, tag_name, tag_length, tag_parser):
        self.tag_name = tag_name
        self.tag_length = tag_length
        self.tag_parser = tag_parser

    def parse(self, stream, name):
        payload_length = int.from_bytes(stream.read(4), byteorder='big', signed=True)
        tag = MultiNBTTag(self.tag_name + "Array", name)
        for i in range(payload_length):
            tag.addChild(
                DataNBTTag(
                    self.tag_name, 
                    "None", 
                    struct.unpack(
                        self.tag_parser, 
                        stream.read(self.tag_length)
                    )[0]
                )
            )
        return tag

class _ListParser:
    def parse(self, stream, name):
        global _parsers

        sub_type = int.from_bytes(stream.read(1), byteorder='big', signed=False)
        payload_length = int.from_bytes(stream.read(4), byteorder='big', signed=True)
        tag = MultiNBTTag("List", name)
        for i in range(payload_length):
            tag.addChild(_parsers[sub_type].parse(stream, "None"))
        return tag

class _CompundParser:
    def parse(self, stream, name):
        tag = CompundNBTTag("Compund", name)
        while stream.peek() != 0: # end tag
            tag.addChild(parse_nbt(stream))
        stream.read(1) # get rid of the end tag
        return tag

class _StringParser:
    def parse(self, stream, name):
        payload_length = int.from_bytes(stream.read(2), byteorder='big', signed=False)
        payload = stream.read(payload_length).decode("utf-8")
        return DataNBTTag("String", name, payload)

_parsers = {
    1: _DataParser("Byte", 1, ">b"),
    2: _DataParser("Short", 2, ">h"),
    3: _DataParser("Int", 4, ">i"),
    4: _DataParser("Long", 8, ">q"),
    5: _DataParser("Float", 4, ">f"),
    6: _DataParser("Double", 8, ">d"),
    7: _ArrayParser("Byte", 1, ">b"),
    8: _StringParser(),
    9: _ListParser(),
    10: _CompundParser(),
    11: _ArrayParser("Int", 4, ">i"),
    12: _ArrayParser("Long", 8, ">q")
}

class DataNBTTag:
    def __init__(self, tag_type, tag_name, tag_value):
        self.tag_type = tag_type
        self.tag_name = tag_name
        self.tag_value = tag_value

    def print(self, indent=""):
        print(indent + self.tag_type + ": '" + self.tag_name + "' = " + str(self.tag_value))

    def get(self):
        return self.tag_value

    def name(self):
        return self.tag_name

class MultiNBTTag:
    def __init__(self, tag_type, tag_name):
        self.tag_type = tag_type
        self.tag_name = tag_name
        self.children = []
    
    def addChild(self, tag):
        self.children.append(tag)
    
    def name(self):
        return self.tag_name

    def print(self, indent=""):
        print(indent + self.tag_type + ": '" + self.tag_name + "' size " + str(len(self.children)))
        for c in self.children:
            c.print(indent + "  ")

class CompundNBTTag(MultiNBTTag):
    def __init__(self, tag_type, tag_name):
        self.tag_type = tag_type
        self.tag_name = tag_name
        self.children = {}

    def addChild(self, tag):
        self.children[tag.tag_name] = tag

    def get(self, name):
        return self.children[name]

    def name(self):
        return self.tag_name

    def has(self, name):
        return name in self.children

    def toDict(self):
        nd = {}
        for p in self.children:
            nd[p] = self.children[p].get()
        return nd

    def print(self, indent=""):
        print(indent + self.tag_type + ": '" + self.tag_name + "' size " + str(len(self.children)))
        for c in self.children:
            self.children[c].print(indent + "  ")

def parse_nbt(stream):
    global _parsers

    tag_type = int.from_bytes(stream.read(1), byteorder='big', signed=False)
    tag_name_length = int.from_bytes(stream.read(2), byteorder='big', signed=False)
    tag_name = stream.read(tag_name_length).decode("utf-8")

    return _parsers[tag_type].parse(stream, tag_name)

