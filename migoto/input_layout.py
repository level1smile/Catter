from ..utils.migoto_utils import *

import io
import textwrap
import collections
import math


class InputLayoutElement(object):
    SemanticName = ""
    SemanticIndex = ""
    Format = ""
    AlignedByteOffset = ""
    InputSlotClass = ""
    ElementName = ""

    def __init__(self, arg):
        if isinstance(arg, io.IOBase):
            self.from_file(arg)
        else:
            self.from_dict(arg)

        self.encoder, self.decoder = EncoderDecoder(self.Format)
    
    def read_attribute_line(self, f) -> bool:
        line = next(f).strip()
        if line.startswith('SemanticName: '):
            self.SemanticName = line[len('SemanticName: ') :]
            # print("SemanticName:" + self.SemanticName)
        elif line.startswith('SemanticIndex: '):
            self.SemanticIndex = line[len('SemanticIndex: ') :]
            # print("SemanticIndex:" + self.SemanticIndex)
            self.SemanticIndex = int(self.SemanticIndex)
        elif line.startswith('Format: '):
            self.Format = line[len('Format: '):]
            # print("Format:" + self.Format)
        elif line.startswith('AlignedByteOffset: '):
            self.AlignedByteOffset = line[len('AlignedByteOffset: ') :]
            # print("AlignedByteOffset:" + self.AlignedByteOffset)
            if self.AlignedByteOffset == 'append':
                raise Fatal('Input layouts using "AlignedByteOffset=append" are not yet supported')
            self.AlignedByteOffset = int(self.AlignedByteOffset)
        elif line.startswith('InputSlotClass: '):
            self.InputSlotClass = line[len('InputSlotClass: ') :]
            # print("InputSlotClass:" + self.InputSlotClass)
            # return false if we meet end of all element
            return False
        return True
        
        
    def from_file(self, f):
        while(self.read_attribute_line(f)):
            pass
        self.format_len = format_components(self.Format)
        if self.SemanticIndex != 0:
            self.ElementName = self.SemanticName + str(self.SemanticIndex)
        else:
            self.ElementName = self.SemanticName 

    def to_dict(self):
        d = {'SemanticName': self.SemanticName, 'SemanticIndex': self.SemanticIndex, 'Format': self.Format,
             'AlignedByteOffset': self.AlignedByteOffset,
             'InputSlotClass': self.InputSlotClass,
             'ElementName':self.ElementName}
        return d

    def to_string(self, indent=2):
        return textwrap.indent(textwrap.dedent('''
            SemanticName: %s
            SemanticIndex: %i
            Format: %s
            AlignedByteOffset: %i
            InputSlotClass: %s
            ElementName: %s
        ''').lstrip() % (
            self.SemanticName,
            self.SemanticIndex,
            self.Format,
            self.AlignedByteOffset,
            self.InputSlotClass,
            self.ElementName
        ), ' ' * indent)

    def from_dict(self, d):
        self.SemanticName = d['SemanticName']
        self.SemanticIndex = d['SemanticIndex']
        self.Format = d['Format']
        self.AlignedByteOffset = d['AlignedByteOffset']
        self.InputSlotClass = d['InputSlotClass']
        self.ElementName = d['ElementName']
        self.format_len = format_components(self.Format)

    @property
    def name(self):
        if self.SemanticIndex:
            return '%s%i' % (self.SemanticName, self.SemanticIndex)
        return self.SemanticName

    def pad(self, data, val):
        padding = self.format_len - len(data)
        assert (padding >= 0)
        data.extend([val] * padding)
        return data 

    def clip(self, data):
        return data[:format_components(self.Format)]

    def size(self):
        return format_size(self.Format)

    def is_float(self):
        return misc_float_pattern.match(self.Format)

    def is_int(self):
        return misc_int_pattern.match(self.Format)

    def encode(self, data):
        # print(self.Format, data)
        return self.encoder(data)

    def decode(self, data):
        return self.decoder(data)

    def __eq__(self, other):
        return \
                self.SemanticName == other.SemanticName and \
                self.SemanticIndex == other.SemanticIndex and \
                self.Format == other.Format and \
                self.AlignedByteOffset == other.AlignedByteOffset and \
                self.InputSlotClass == other.InputSlotClass 


class InputLayout(object):
    def __init__(self, custom_prop=[], stride=0):
        self.elems = collections.OrderedDict()
        self.stride = stride
        for item in custom_prop:
            elem = InputLayoutElement(item)
            self.elems[elem.name] = elem

    def serialise(self):
        return [x.to_dict() for x in self.elems.values()]

    def to_string(self):
        ret = ''
        for i, elem in enumerate(self.elems.values()):
            ret += 'element[%i]:\n' % i
            ret += elem.to_string()
        return ret

    def parse_element(self, f):
        elem = InputLayoutElement(f)
        self.elems[elem.name] = elem

    def __iter__(self):
        return iter(self.elems.values())

    def __getitem__(self, semantic):
        return self.elems[semantic]

    def encode(self, vertex):
        buf = bytearray(self.stride)

        for semantic, data in vertex.items():
            if semantic.startswith('~'):
                continue
            elem = self.elems[semantic]
            data = elem.encode(data)
            buf[elem.AlignedByteOffset:elem.AlignedByteOffset + len(data)] = data

        assert (len(buf) == self.stride)
        return buf

    def decode(self, buf):
        vertex = {}
        for elem in self.elems.values():
            data = buf[elem.AlignedByteOffset:elem.AlignedByteOffset + elem.size()]
            vertex[elem.name] = elem.decode(data)
        return vertex

    def __eq__(self, other):
        return self.elems == other.elems

