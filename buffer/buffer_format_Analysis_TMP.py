# Learned from ShaderFreedom discord @Aiden

import math
import bpy
import struct
import itertools
import re
import bmesh


# This used to catch any exception in run time and raise it to blender output console.
class Fatal(Exception):
    pass



import math
import bpy
import struct
import itertools
import re
import bmesh

def extract_drawindexed_values(ini_file):
    object_data = []
    with open(ini_file, 'r') as file:
        lines = file.readlines()
    
    current_component = None
    component_sums = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('; Draw Component'):
            component_number = extract_component_number(line)
            if component_number is not None:
                current_component = component_number
                if current_component not in component_sums:
                    component_sums[current_component] = (0, None)
        
        if line.startswith('drawindexed'):
            values = re.findall(r'\d+', line)
            if len(values) >= 2:
                value1 = int(values[0])
                value2 = int(values[1])
                if current_component is not None:
                    current_sum, existing_second_value = component_sums[current_component]
                    component_sums[current_component] = (current_sum + value1, existing_second_value if existing_second_value is not None else value2)
    
    for component_number, (sum_value, second_value) in component_sums.items():
        if second_value is not None:
            object_data.append((sum_value, second_value))
    
    return object_data

def extract_component_number(line):
    # Find the part after "; Draw Component"
    match = re.search(r'; Draw Component\s+(\d+)', line)
    if match:
        return int(match.group(1))
    return None

def read_position_buffer(file_path):
    vertices = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(12):  # DXGI_FORMAT_R32G32B32_FLOAT uses 12 bytes per vertex
            x, y, z = struct.unpack('<3f', chunk)
            vertices.append((x, y, z))
    return vertices

def read_index_buffer(file_path):
    indices = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(4):  # Assuming indices are packed as 4 bytes each
            index = struct.unpack('<I', chunk)[0]
            indices.append(index)
    return indices

def read_vector_buffer(file_path):
    tangents = []
    normals = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):  # 8 bytes per record for tangents and normals
            if len(chunk) == 8:
                # Extract Tangent (4 bytes for x, y, z, w)
                tx, ty, tz, tw = struct.unpack('<4b', chunk[0:4])
                tangents.append((tx / 127.0, ty / 127.0, tz / 127.0, tw / 127.0))
                
                # Extract Normal (4 bytes for x, y, z, w)
                nx, ny, nz, nw = struct.unpack('<4b', chunk[4:8])
                normals.append((nx / 127.0, ny / 127.0, nz / 127.0, nw / 127.0))
    return tangents, normals

def read_texcoord_buffer(file_path):
    texcoords0 = []
    texcoords1 = []
    texcoords2 = []
    color1 = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(16):  # 16 bytes per record
            if len(chunk) == 16:
                u0, v0 = struct.unpack('<2e', chunk[0:4])
                texcoords0.append((u0, v0))               
                # Extract Color1 (4 bytes for r and g)
                r1, g1 = struct.unpack('<2H', chunk[4:8])
                color1.append((r1 / 65535.0, g1 / 65535.0, 0.0, 0.0))  # Use normalized value
                u1, v1 = struct.unpack('<2e', chunk[8:12])
                texcoords1.append((u1, v1))
                u2, v2 = struct.unpack('<2e', chunk[12:16])
                texcoords2.append((u2, v2))
    
    return texcoords0, texcoords1, texcoords2, color1

def read_color_buffer(file_path):
    color0 = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(4):  # DXGI_FORMAT_R8G8B8A8_UNORM uses 4 bytes per color
            r, g, b, a = struct.unpack('<4B', chunk)
            color0.append((r / 255.0, g / 255.0, b / 255.0, a / 255.0))
    return color0

def read_blend_buffer(file_path):
    blend_indices = []
    blend_weights = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):  # 8 bytes per record (4 bytes for indices + 4 bytes for weights)
            if len(chunk) == 8:
                indices = struct.unpack('<4B', chunk[:4])  # 4 bytes for blend indices
                weights = struct.unpack('<4B', chunk[4:])  # 4 bytes for blend weights
                blend_indices.append(indices)
                blend_weights.append(weights)
    blend_weights = normalize_weights(blend_weights)
    return blend_indices, blend_weights

def normalize_weights(weights):
    normalized_weights = []
    for weight_set in weights:
        total_weight = sum(weight_set)
        if total_weight > 0:
            normalized_weights.append(tuple(w / total_weight for w in weight_set))
        else:
            normalized_weights.append(weight_set)  # Avoid division by zero
    return normalized_weights

def read_shape_key_offset(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()

    # R32_UINT长度固定为4
    num_integers = len(data) // 4
    # 得到unpack读取所需格式字符串,表示要读取这么多个数量的UINT_32数据 
    # 这里固定为128个
    format_string = '<' + 'I' * num_integers
    unpacked_data = struct.unpack(format_string, data)
    
    if len(unpacked_data) > 1:
        unique_data = []
        seen = {}
        # 这里反转是要从后往前读，每个数据出现两次避免遗漏最后一个
        for value in reversed(unpacked_data):
            if value not in seen: # 没出现过就增加并设为出现过
                seen[value] = 1
                unique_data.append(value)
            elif seen[value] < 2: # 出现过1次，就增加并且后续出现不再判断
                seen[value] += 1
                unique_data.append(value)
        unique_data.reverse()
        
        unpacked_data = unique_data
    
    return unpacked_data

def read_shape_key_vertex_id(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    # UINT_32
    num_ids = len(data) // 4
    format_string = '<' + 'I' * num_ids
    return struct.unpack(format_string, data)

def read_shape_key_vertex_offset(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    num_offsets = len(data) // 2
    format_string = '<' + 'e' * num_offsets
    offsets = struct.unpack(format_string, data)

    cleaned_offsets = []
    for i in range(0, len(offsets), 3):
        triplet = offsets[i:i+3]
        if triplet != (0.0, 0.0, 0.0):
            # extend()是把每个元素逐个追加到列表结尾。
            # 这里函数的作用就是删掉所有为0的数据，只保留基础数据。
            cleaned_offsets.extend(triplet)

    return cleaned_offsets

def import_uv_layers(mesh, texcoords):
    uv_layers_data = [
        ("TEXCOORD.xy", texcoords[0]),  # TexCoord0
        ("TEXCOORD1.xy", texcoords[1]),  # TexCoord1
        ("TEXCOORD2.xy", texcoords[2])   # TexCoord2
    ]

    for uv_name, uv_data in uv_layers_data:
        if uv_data:
            uv_layer = mesh.uv_layers.new(name=uv_name)
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]
                    loop_vertex_index = loop.vertex_index

                    if loop_vertex_index < len(uv_data):
                        uv = uv_data[loop_vertex_index]
                        uv_layer.data[loop_index].uv = (uv[0], 1.0 - uv[1])  # Flip V if necessary
                    else:
                        uv_layer.data[loop_index].uv = (0.0, 0.0)

            print(f"UV Layer '{uv_name}' imported successfully.")

def import_vertex_groups(mesh, obj, blend_indices, blend_weights, component=None):
    if len(blend_indices) != len(blend_weights):
        raise ValueError("Mismatch between blend_indices and blend_weights lengths")
    
    connected_vertex_ids = set()
    for poly in mesh.polygons:
        connected_vertex_ids.update(poly.vertices)
    
    connected_blend_indices = set()
    for vertex_index, indices in enumerate(blend_indices):
        if vertex_index in connected_vertex_ids:
            connected_blend_indices.update(indices)
    if component is None:
        num_vertex_groups = max(connected_blend_indices) + 1 if connected_blend_indices else 0
    else:
        num_vertex_groups = max(component.vg_map[i] for i in connected_blend_indices) + 1 if connected_blend_indices else 0
        vg_map = list(map(int, component.vg_map.values()))
    
    vertex_groups = [obj.vertex_groups.new(name=str(i)) for i in range(num_vertex_groups)]
    
    if component is None:
        group_map = {i: vertex_groups[i] for i in connected_blend_indices}
    else:
        group_map = {i: vertex_groups[vg_map[i]] for i in connected_blend_indices}
    
    vertex_weight_map = {v.index: [] for v in mesh.vertices}
    for vertex_index, indices in enumerate(blend_indices):
        weights = blend_weights[vertex_index]
        if vertex_index in connected_vertex_ids and vertex_index in vertex_weight_map:
            for idx, weight in zip(indices, weights):
                if weight > 0.0:
                    vertex_weight_map[vertex_index].append((idx, weight))
    for vertex in mesh.vertices:
        if vertex.index in vertex_weight_map and vertex.index in connected_vertex_ids:
            for idx, weight in vertex_weight_map[vertex.index]:
                group_map[idx].add([vertex.index], weight, 'REPLACE')
    for vg in obj.vertex_groups:
        num_vertices = sum(1 for v in mesh.vertices if vertex_weight_map.get(v.index, []))
        print(f"Vertex Group '{vg.name}' has {num_vertices} vertices assigned.")


def apply_normals(obj, mesh, normals):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    if len(normals) != len(mesh.vertices):
        raise ValueError("Number of normals must match the number of vertices.")
    
    # https://docs.blender.org/api/3.6/bpy.types.Mesh.html#bpy.types.Mesh.normals_split_custom_set_from_vertices
    # 这里避免了create_normal_splits()的使用
    mesh.normals_split_custom_set_from_vertices([normal[:3] for normal in normals])
    mesh.update()
    
    # 使用bmesh在faces属性中调用normal_flip()来翻转法线
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    fmesh = bmesh.from_edit_mesh(obj.data)
    for face in fmesh.faces:
        face.normal_flip()
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.update()
    
    # 但是这里调用了calc_normals_split()
    mesh.calc_normals_split()
    mesh.update()
    
    # 调用faces_shade_smooth()设置自动平滑着色
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    obj.data.update()

def apply_tangents(mesh, tangents):
    if len(tangents) != len(mesh.vertices):
        raise ValueError("Number of tangents must match the number of vertices.")
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="TANGENT")
    mesh.update()

def import_shapekeys(obj, shapekey_offsets, shapekey_vertex_ids, shapekey_vertex_offsets, scale_factor=1.0):
    if len(shapekey_offsets) == 0:
        return

    # Ensure the object is in object mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get the mesh data
    mesh = obj.data
    vertices = mesh.vertices
    polygons = mesh.polygons

    # Create a set of vertex indices that are part of the mesh (linked to any polygon)
    existing_vertex_ids = set()
    for poly in polygons:
        existing_vertex_ids.update(poly.vertices)

    # Import shapekeys
    num_shapekeys = len(shapekey_offsets) # 形态键数量
    basis_shapekey_added = False

    for i in range(num_shapekeys):
        start_offset = shapekey_offsets[i] # 当前内容为起始索引
        # end_offset = shapekey_offsets[i + 1] if i + 1 < num_shapekeys else len(shapekey_vertex_ids)
        if num_shapekeys > i + 1:
            end_offset = shapekey_offsets[i + 1] # 结束索引为 下一个
        else:
            end_offset = len(shapekey_vertex_ids) 
        
        # Check if there are any valid vertices for this shapekey
        # 用读取到的vertex_id在当前mesh的vertex_id中查找，如果找到了就has_valid_vertices说明是含有有效顶点
        # 说明当前形态键的id值里有mesh的id值
        has_valid_vertices = any(vertex_id in existing_vertex_ids for vertex_id in shapekey_vertex_ids[start_offset:end_offset])
        
        if not has_valid_vertices:
            continue

        # Add the basis shapekey if it hasn't been added yet
        # 添加一个Basis作为基础形态，只能添加一次。
        if not basis_shapekey_added:
            basis_shapekey = obj.shape_key_add(name='Basis')
            basis_shapekey.interpolation = 'KEY_LINEAR'
            obj.data.shape_keys.use_relative = True
            basis_shapekey_added = True
        
        # Add new shapekey
        shapekey = obj.shape_key_add(name=f'Deform {i}')
        shapekey.interpolation = 'KEY_LINEAR'

        # Apply shapekey vertex position offsets to each indexed vertex
        for j in range(start_offset, end_offset):
            vertex_id = shapekey_vertex_ids[j]
            index = j * 3
            if index + 3 <= len(shapekey_vertex_offsets):  # Ensure indices are within bounds
                position_offset = shapekey_vertex_offsets[index:index + 3]
                
                # Scale the offsets
                position_offset = [scale_factor * offset for offset in position_offset]
                if vertex_id in existing_vertex_ids and vertex_id < len(shapekey.data):  # Check if vertex is part of the mesh and exists in the shapekey
                    shapekey.data[vertex_id].co.x += position_offset[0]
                    shapekey.data[vertex_id].co.y += position_offset[1]
                    shapekey.data[vertex_id].co.z += position_offset[2]

                    
def create_mesh_from_buffers(vertices, indices, texcoords, color0, color1, object_data, blend_weights, blend_indices, normals,tangents, shapekey_offsets, shapekey_vertex_ids, shapekey_vertex_offsets,component=None):
    flip_texcoord_v = False  # Set this to True if V should be flipped

    for i, (count, start_index) in enumerate(object_data):
        # Create the mesh and object
        mesh = bpy.data.meshes.new(name=f"Component {i}")
        obj = bpy.data.objects.new(name=f"Component {i}", object_data=mesh)
        bpy.context.collection.objects.link(obj)

        # Create faces
        end_index = start_index + count
        if end_index > len(indices):
            end_index = len(indices)  # Adjust to avoid index out of range

        faces = [(indices[j], indices[j+1], indices[j+2]) for j in range(start_index, end_index - 2, 3)]
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        if color0:
            color_layer0 = mesh.vertex_colors.new(name="COLOR")
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]
                    loop_vertex_index = loop.vertex_index
                    if loop_vertex_index < len(color0):
                        color_layer0.data[loop_index].color = color0[loop_vertex_index]

        if color1:
            color_layer1 = mesh.vertex_colors.new(name="COLOR1")
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    loop = mesh.loops[loop_index]
                    loop_vertex_index = loop.vertex_index
                    if loop_vertex_index < len(color1):
                        color_layer1.data[loop_index].color = color1[loop_vertex_index]

        import_uv_layers(mesh, texcoords)
        if blend_weights and blend_indices:
            import_vertex_groups(mesh, obj, blend_indices, blend_weights, component)
        apply_tangents(mesh, tangents)
        apply_normals(obj, mesh, normals)
        # Remove loose vertices
        import_shapekeys(obj,shapekey_offsets, shapekey_vertex_ids, shapekey_vertex_offsets)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete_loose()
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.scale = (0.01, 0.01, 0.01)
        obj.rotation_euler[2] = math.radians(180)

        print(f"Mesh {i} created successfully.")
# def main():
#     # Paths to the .buf files
#     base_path = 'F:/WuwaMods/Mods/changlimod/'
#     position_buf_path = base_path + '/meshes/Position.buf'
#     index_buf_path = base_path + '/meshes/index.buf'
#     texcoord_buf_path = base_path + '/meshes/Texcoord.buf'
#     color_buf_path = base_path + '/meshes/color.buf'
#     blend_buf_path = base_path + '/meshes/blend.buf'
#     vector_buf_path = base_path + '/meshes/Vector.buf'
#     shape_key_offset_file = base_path + '/meshes/ShapeKeyOffset.buf'
#     shape_key_vertex_id_file = base_path + '/meshes/ShapeKeyVertexId.buf'
#     shape_key_vertex_offset_file = base_path + '/meshes/ShapeKeyVertexOffset.buf'
#     ini_file_path = base_path + 'mod.ini'
#     object_data = extract_drawindexed_values(ini_file_path) # if mod has weird toggles add drawindeces manually
    
#     vertices = read_position_buffer(position_buf_path)
#     indices = read_index_buffer(index_buf_path)
#     texcoords0, texcoords1, texcoords2, color1 = read_texcoord_buffer(texcoord_buf_path)
#     color0 = read_color_buffer(color_buf_path)
#     blend_indices, blend_weights = read_blend_buffer(blend_buf_path)
#     tangents, normals = read_vector_buffer(vector_buf_path)    
#     texcoords = [texcoords0, texcoords1, texcoords2]
#     shapekey_offsets = read_shape_key_offset(shape_key_offset_file)
#     shapekey_vertex_ids = read_shape_key_vertex_id(shape_key_vertex_id_file)
#     shapekey_vertex_offsets = read_shape_key_vertex_offset(shape_key_vertex_offset_file)
    
#     create_mesh_from_buffers(vertices, indices, texcoords, color0, color1, object_data, blend_weights, blend_indices, normals, tangents, shapekey_offsets, shapekey_vertex_ids, shapekey_vertex_offsets)



