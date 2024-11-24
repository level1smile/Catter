from .migoto_utils import *

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

    def to_dict(self):
        d = {'SemanticName': self.SemanticName, 'SemanticIndex': self.SemanticIndex, 'Format': self.Format,
             'AlignedByteOffset': self.AlignedByteOffset,
             'InputSlotClass': self.InputSlotClass}
        return d

    def to_string(self, indent=2):
        return textwrap.indent(textwrap.dedent('''
            SemanticName: %s
            SemanticIndex: %i
            Format: %s
            AlignedByteOffset: %i
            InputSlotClass: %s
        ''').lstrip() % (
            self.SemanticName,
            self.SemanticIndex,
            self.Format,
            self.AlignedByteOffset,
            self.InputSlotClass,
        ), ' ' * indent)

    def from_dict(self, d):
        self.SemanticName = d['SemanticName']
        self.SemanticIndex = d['SemanticIndex']
        self.Format = d['Format']
        self.AlignedByteOffset = d['AlignedByteOffset']
        self.InputSlotClass = d['InputSlotClass']
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


class VertexBuffer(object):
    vb_elem_pattern = re.compile(r'''vb\d+\[\d*\]\+\d+ (?P<semantic>[^:]+): (?P<data>.*)$''')

    # Python gotcha - do not set layout=InputLayout() in the default function
    # parameters, as they would all share the *same* InputLayout since the
    # default values are only evaluated once on file load
    def __init__(self, f=None, layout=None):
        self.vertices = []
        self.layout = layout and layout or InputLayout()
        self.first = 0
        self.vertex_count = 0
        self.offset = 0
        self.topology = 'trianglelist'

        if f is not None:
            self.parse_vb_txt(f)

    def parse_vb_txt(self, f):
        for line in map(str.strip, f):
            # print(line)
            if line.startswith('byte offset:'):
                self.offset = int(line[13:])
            if line.startswith('first vertex:'):
                self.first = int(line[14:])
            if line.startswith('vertex count:'):
                self.vertex_count = int(line[14:])
            if line.startswith('stride:'):
                self.layout.stride = int(line[7:])
            if line.startswith('element['):
                self.layout.parse_element(f)
            if line.startswith('topology:'):
                self.topology = line[10:]
                if line != 'topology: trianglelist':
                    raise Fatal('"%s" is not yet supported' % line)
        assert (len(self.vertices) == self.vertex_count)

    def parse_vb_bin(self, f):
        f.seek(self.offset)
        # XXX: Should we respect the first/base vertex?
        # f.seek(self.first * self.layout.stride, whence=1)
        self.first = 0
        while True:
            vertex = f.read(self.layout.stride)
            if not vertex:
                break
            self.vertices.append(self.layout.decode(vertex))
        self.vertex_count = len(self.vertices)

    def append(self, vertex):
        self.vertices.append(vertex)
        self.vertex_count += 1

    def parse_vertex_element(self, match):
        fields = match.group('data').split(',')

        if self.layout[match.group('semantic')].Format.endswith('INT'):
            return tuple(map(int, fields))

        return tuple(map(float, fields))

    def write(self, output, operator=None):
        for vertex in self.vertices:
            output.write(self.layout.encode(vertex))

        msg = 'Wrote %i vertices to %s' % (len(self), output.name)
        if operator:
            operator.report({'INFO'}, msg)
        else:
            print(msg)

    def __len__(self):
        return len(self.vertices)
    

        # 向量归一化
    def vector_normalize(self,v):
        """归一化向量"""
        length = math.sqrt(sum(x * x for x in v))
        if length == 0:
            return v  # 避免除以零
        return [x / length for x in v]
    
    def add_and_normalize_vectors(self,v1, v2):
        """将两个向量相加并规范化(normalize)"""
        # 相加
        result = [a + b for a, b in zip(v1, v2)]
        # 归一化
        normalized_result = self.vector_normalize(result)
        return normalized_result
    
    # Nico: 向量相加归一化法线 
    def get_position_normalizednormal_dict(self,vertices):
        position_normal_dict = {}
        for vertex in vertices:
            position = vertex["POSITION"]
            position_str = str(position[0]) + "_" + str(position[1]) + "_" + str(position[2])

            normal = vertex["NORMAL"]
            if position_str in position_normal_dict:
                normalized_normal = self.add_and_normalize_vectors(normal,position_normal_dict[position_str])
                position_normal_dict[position_str] = normalized_normal
            else:
                position_normal_dict[position_str] = normal
        return position_normal_dict
    
    # Nico: 算数平均归一化法线，HI3 2.0角色使用的方法
    def get_position_averagenormal_dict(self,vertices):
        position_normal_sum_dict = {}
        position_normal_number_dict = {}

        for vertex in vertices:
            position = vertex["POSITION"]
            position_str = str(position[0]) + "_" + str(position[1]) + "_" + str(position[2])
            normal = vertex["NORMAL"]
            if position_str in position_normal_sum_dict:
                normal_sum = [a + b for a, b in zip(normal, position_normal_sum_dict[position_str])]
                position_normal_sum_dict[position_str] = normal_sum
                position_normal_number_dict[position_str] = position_normal_number_dict[position_str] + 1
            else:
                position_normal_sum_dict[position_str] = normal
                position_normal_number_dict[position_str] = 1

        
        position_normal_dict = {}
        for k, v in position_normal_sum_dict.items():
            number = float(position_normal_number_dict[k])
            # Nico: 平均后的值+1后再除以2，就归一化到[0,1]了 这个归一化是逆向分析HI3 2.0新角色模型得到的。
            average_normal = [((x / number) + 1 ) / 2 for x in v] 
            position_normal_dict[k] = average_normal

        return position_normal_dict

    # 辅助函数：计算两个向量的点积
    def dot_product(self,v1, v2):
        return sum(a * b for a, b in zip(v1, v2))

    # Nico: 米游所有游戏都能用到这个，还有曾经的GPU-PreSkinning的GF2也会用到这个，崩坏三2.0新角色除外。
    def vector_normalized_normal_to_tangent(self):
        position_normal_dict = self.get_position_normalizednormal_dict(self.vertices)
        new_vertices = []


        for vertex in self.vertices:
            position = vertex["POSITION"]
            position_str = str(position[0]) + "_" + str(position[1]) + "_" + str(position[2])
            if position_str in position_normal_dict:
                normalized_normal = position_normal_dict[position_str]

                # 计算副切线
                tangent = vertex["TANGENT"][:3]
                binormal = self.vector_normalize([
                    normalized_normal[1] * tangent[2] - normalized_normal[2] * tangent[1],
                    normalized_normal[2] * tangent[0] - normalized_normal[0] * tangent[2],
                    normalized_normal[0] * tangent[1] - normalized_normal[1] * tangent[0]
                ])
                # 确定W分量
                w = 1.0 if self.dot_product(binormal, vertex.get("BINORMAL", [0, 0, 1])) >= 0.0 else -1.0
                    
                # 最终赋值
                vertex["TANGENT"][0] = normalized_normal[0]
                vertex["TANGENT"][1] = normalized_normal[1]
                vertex["TANGENT"][2] = normalized_normal[2]
                if bpy.context.scene.dbmt.flip_tangent_w:
                    vertex["TANGENT"][3] = -1 * w
                else:
                    vertex["TANGENT"][3] = w
                new_vertices.append(vertex)

        self.vertices = new_vertices

    def arithmetic_average_normal_to_attribute(self,attribute):
        position_normal_dict = self.get_position_averagenormal_dict(self.vertices)
        new_vertices = []
        for vertex in self.vertices:
            position = vertex["POSITION"]
            position_str = str(position[0]) + "_" + str(position[1]) + "_" + str(position[2])
            if position_str in position_normal_dict:
                normalized_normal = position_normal_dict[position_str]
                vertex[attribute][0] = normalized_normal[0]
                vertex[attribute][1] = normalized_normal[1]
                vertex[attribute][2] = normalized_normal[2]
                new_vertices.append(vertex)

        self.vertices = new_vertices

    # Nico: 目前出现的游戏中只有崩坏三2.0新角色会用到这个
    def arithmetic_average_normal_to_color(self):
        self.arithmetic_average_normal_to_attribute("COLOR")


class IndexBuffer(object):
    def __init__(self, *args):
        self.faces = []
        self.first = 0
        self.index_count = 0
        self.format = 'DXGI_FORMAT_UNKNOWN'
        self.offset = 0
        self.topology = 'trianglelist'

        if isinstance(args[0], io.IOBase):
            assert (len(args) == 1)
            self.parse_fmt(args[0])
        else:
            self.format, = args

        self.encoder, self.decoder = EncoderDecoder(self.format)

    def append(self, face):
        self.faces.append(face)
        self.index_count += len(face)

    def parse_fmt(self, f):
        for line in map(str.strip, f):
            if line.startswith('byte offset:'):
                self.offset = int(line[13:])
            if line.startswith('first index:'):
                self.first = int(line[13:])
            elif line.startswith('index count:'):
                self.index_count = int(line[13:])
            elif line.startswith('topology:'):
                self.topology = line[10:]
                if line != 'topology: trianglelist':
                    raise Fatal('"%s" is not yet supported' % line)
            elif line.startswith('format:'):
                self.format = line[8:]
            elif line == '':
                    return
        assert (len(self.faces) * 3 == self.index_count)

    def parse_ib_bin(self, f):
        f.seek(self.offset)
        stride = format_size(self.format)
        # XXX: Should we respect the first index?
        # f.seek(self.first * stride, whence=1)
        self.first = 0

        face = []
        while True:
            index = f.read(stride)
            if not index:
                break
            face.append(*self.decoder(index))
            if len(face) == 3:
                self.faces.append(tuple(face))
                face = []
        assert (len(face) == 0)

        # We intentionally disregard the index count when loading from a
        # binary file, as we assume frame analysis might have only dumped a
        # partial buffer to the .txt files (e.g. if this was from a dump where
        # the draw call index count was overridden it may be cut short, or
        # where the .txt files contain only sub-meshes from each draw call and
        # we are loading the .buf file because it contains the entire mesh):
        self.index_count = len(self.faces) * 3


    def write(self, output, operator=None):
        for face in self.faces:
            output.write(self.encoder(face))

        msg = 'Wrote %i indices to %s' % (len(self), output.name)
        if operator:
            operator.report({'INFO'}, msg)
        else:
            print(msg)

    def __len__(self):
        return len(self.faces) * 3