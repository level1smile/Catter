from .migoto_format import *

import json
import os.path
import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty, StringProperty


# from export_obj:
def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def blender_vertex_to_3dmigoto_vertex(mesh, obj, blender_loop_vertex, layout:InputLayout, texcoords):
    # 根据循环顶点中的顶点索引来从总的顶点中获取对应的顶点
    blender_vertex = mesh.vertices[blender_loop_vertex.vertex_index]
    vertex = {}

    # ignoring groups with weight=0.0
    vertex_groups = sorted(blender_vertex.groups, key=lambda x: x.weight, reverse=True)

    for elem in layout:
        # 只处理per-vertex的
        if elem.InputSlotClass != 'per-vertex':
            continue

        if elem.name == 'POSITION':
            vertex[elem.name] = elem.pad(list(blender_vertex.undeformed_co), 1.0)

        elif elem.name.startswith('COLOR'):
            if elem.name in mesh.vertex_colors:
                vertex[elem.name] = elem.clip(list(mesh.vertex_colors[elem.name].data[blender_loop_vertex.index].color))
            else:
                vertex[elem.name] = list(mesh.vertex_colors[elem.name + '.RGB'].data[blender_loop_vertex.index].color)[
                                    :3] + \
                                    [mesh.vertex_colors[elem.name + '.A'].data[blender_loop_vertex.index].color[0]]
        elif elem.name == 'NORMAL':
            vertex[elem.name] = elem.pad(list(blender_loop_vertex.normal), 0.0)

            if bpy.context.scene.dbmt.flip_normal_x:
                vertex[elem.name][0] = -1 * vertex[elem.name][0]
            if bpy.context.scene.dbmt.flip_normal_y:
                vertex[elem.name][1] = -1 * vertex[elem.name][1]
            if bpy.context.scene.dbmt.flip_normal_z:
                vertex[elem.name][2] = -1 * vertex[elem.name][2]
            if bpy.context.scene.dbmt.flip_normal_w:
                if len(vertex[elem.name]) == 4:
                    vertex[elem.name][3] = -1 * vertex[elem.name][3]

        elif elem.name.startswith('TANGENT'):
            # Nico: Unity games need to flip TANGENT.w to get perfect shadow.
            vertex[elem.name] = elem.pad(list(blender_loop_vertex.tangent), blender_loop_vertex.bitangent_sign)
            if bpy.context.scene.dbmt.flip_tangent_x:
                vertex[elem.name][0] = -1 * vertex[elem.name][0]
            if bpy.context.scene.dbmt.flip_tangent_y:
                vertex[elem.name][1] = -1 * vertex[elem.name][1]
            if bpy.context.scene.dbmt.flip_tangent_z:
                vertex[elem.name][2] = -1 * vertex[elem.name][2]
            if bpy.context.scene.dbmt.flip_tangent_w:
                vertex[elem.name][3] = -1 * vertex[elem.name][3]
                
        elif elem.name.startswith('BLENDINDICES'):
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([x.group for x in vertex_groups[i:i + 4]], 0)
        elif elem.name.startswith('BLENDWEIGHT'):
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([x.weight for x in vertex_groups[i:i + 4]], 0.0)
        elif elem.name.startswith('TEXCOORD') and elem.is_float():
            # FIXME: Handle texcoords of other dimensions
            uvs = []
            for uv_name in ('%s.xy' % elem.name, '%s.zw' % elem.name):
                if uv_name in texcoords:
                    uvs += list(texcoords[uv_name][blender_loop_vertex.index])
            vertex[elem.name] = uvs

        # Nico: 不需要考虑BINORMAL，现代游戏的渲染基本上不会使用BINORMAL这种过时的渲染方案
        # elif elem.name.startswith('BINORMAL'):
            # Some DOA6 meshes (skirts) use BINORMAL, but I'm not certain it is
            # actually the binormal. These meshes are weird though, since they
            # use 4 dimensional positions and normals, so they aren't something
            # we can really deal with at all. Therefore, the below is untested,
            # FIXME: So find a mesh where this is actually the binormal,
            # uncomment the below code and test.
            # normal = blender_loop_vertex.normal
            # tangent = blender_loop_vertex.tangent
            # binormal = numpy.cross(normal, tangent)
            # XXX: Does the binormal need to be normalised to a unit vector?
            # binormal = binormal / numpy.linalg.norm(binormal)
            # vertex[elem.name] = elem.pad(list(binormal), 0.0)
            # pass

        else:
            # Unhandled semantics are saved in vertex layers
            data = []
            for component in 'xyzw':
                layer_name = '%s.%s' % (elem.name, component)
                if layer_name in mesh.vertex_layers_int:
                    data.append(mesh.vertex_layers_int[layer_name].data[blender_loop_vertex.vertex_index].value)
                elif layer_name in mesh.vertex_layers_float:
                    data.append(mesh.vertex_layers_float[layer_name].data[blender_loop_vertex.vertex_index].value)
            if data:
                # print('Retrieved unhandled semantic %s %s from vertex layer' % (elem.name, elem.Format), data)
                vertex[elem.name] = data

        if elem.name not in vertex:
            print('NOTICE: Unhandled vertex element: %s' % elem.name)
        # else:
        #    print('%s: %s' % (elem.name, repr(vertex[elem.name])))

    return vertex


def write_fmt_file(f, vb, ib):
    f.write('stride: %i\n' % vb.layout.stride)
    f.write('topology: %s\n' % vb.topology)
    if ib is not None:
        f.write('format: %s\n' % ib.format)
    f.write(vb.layout.to_string())


class HashableVertex(dict):
    # 旧的代码注释掉了，不过不删，留着用于参考防止忘记原本的设计
    # def __hash__(self):
    #     # Convert keys and values into immutable types that can be hashed
    #     immutable = tuple((k, tuple(v)) for k, v in sorted(self.items()))
    #     return hash(immutable)

    def __hash__(self):
        # 这里将步骤拆分开来，更易于理解
        immutable_items = []
        for k, v in self.items():
            tuple_v = tuple(v)
            pair = (k, tuple_v)
            immutable_items.append(pair)
        sorted_items = sorted(immutable_items)
        immutable = tuple(sorted_items)
        return hash(immutable)



def export_3dmigoto(operator, context, vb_path, ib_path, fmt_path):

    operator.report({'INFO'}, "导出是否保持相同顶点数：" + str(bpy.context.scene.dbmt.export_same_number))
    # 获取当前场景中的obj对象
    obj = context.object

    # 为空时不导出
    if obj is None:
        raise Fatal('No object selected')

    stride = obj['3DMigoto:VBStride']
    layout = InputLayout(obj['3DMigoto:VBLayout'], stride=stride)

    # 获取Mesh
    if hasattr(context, "evaluated_depsgraph_get"):  # 2.80
        mesh = obj.evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
    else:  # 2.79
        mesh = obj.to_mesh(context.scene, True, 'PREVIEW', calc_tessface=False)

    # 使用bmesh复制出一个新mesh并三角化
    mesh_triangulate(mesh)

    try:
        if obj['3DMigoto:IBFormat'] == "DXGI_FORMAT_R16_UINT":
            ib_format = "DXGI_FORMAT_R32_UINT"
        else:
            ib_format = obj['3DMigoto:IBFormat']
    except KeyError:
        ib = None
        raise Fatal('FIXME: Add capability to export without an index buffer')
    else:
        ib = IndexBuffer(ib_format)

    # Calculates tangents and makes loop normals valid (still with our
    # custom normal data from import time):
    # Nico: 这一步如果存在TANGENT属性则会导致顶点数量增加
    mesh.calc_tangents()

    # Nico: 拼凑texcoord层级，有几个UVMap就拼出几个来
    texcoord_layers = {}
    for uv_layer in mesh.uv_layers:
        texcoords = {}

        try:
            flip_texcoord_v = obj['3DMigoto:' + uv_layer.name]['flip_v']
            if flip_texcoord_v:
                flip_uv = lambda uv: (uv[0], 1.0 - uv[1])
            else:
                flip_uv = lambda uv: uv
        except KeyError:
            flip_uv = lambda uv: uv

        for l in mesh.loops:
            uv = flip_uv(uv_layer.data[l.index].uv)
            texcoords[l.index] = uv
        texcoord_layers[uv_layer.name] = texcoords

    # Blender's vertices have unique positions, but may have multiple
    # normals, tangents, UV coordinates, etc - these are stored in the
    # loops. To export back to DX we need these combined together such that
    # a vertex is a unique set of all attributes, but we don't want to
    # completely blow this out - we still want to reuse identical vertices
    # via the index buffer. There might be a convenience function in
    # Blender to do this, but it's easy enough to do this ourselves
    indexed_vertices = collections.OrderedDict()

    unique_position_vertices = {}
    '''
    Nico:
        顶点转换为3dmigoto类型的顶点再经过hashable后，如果存在TANGENT则会导致数量变多，不存在则不会导致数量变多。
        Nico: 初始的Vertex即使是经过TANGENT计算，数量也是和原来一样的
        但是这里使用了blender_lvertex导致了生成的HashableVertex不一样，因为其它都是固定的只有这个blender_lvertex会改变
        需要注意的是如果不计算TANGENT或者没有TANGENT属性时不会额外生成顶点
    '''
    for poly in mesh.polygons:
        face = []
        for blender_lvertex in mesh.loops[poly.loop_start:poly.loop_start + poly.loop_total]:
            #
            vertex = blender_vertex_to_3dmigoto_vertex(mesh, obj, blender_lvertex, layout, texcoord_layers)
            '''
            Nico:
                首先将当前顶点计算为Hash后的顶点然后如果该计算后的Hash顶点不存在，则插入到indexed_vertices里
                随后将该顶点添加到face[]里，索引为该顶点在字典里的索引
                这里我们把获取到的vertex的切线加到一个vertex:切线值的字典中
                如果vertex的顶点在字典中出现了，则返回字典中对应列表和当前值的平均值，否则不进行更新
                这样就能得到每个Position对应的平均切线，在切线值相同的情况下，就不会产生额外的多余顶点了。
                这里我选择简单的使用这个顶点第一次出现的TANGENT作为它的TANGENT，以此避免产生额外多余顶点的问题，后续可以优化为使用平均值作为TANGENT
            '''
            if bpy.context.scene.dbmt.export_same_number:
                if "POSITION" in vertex and "NORMAL" in vertex and "TANGENT" in vertex :
                    if tuple(vertex["POSITION"] + vertex["NORMAL"]  ) in unique_position_vertices:
                        tangent_var = unique_position_vertices[tuple(vertex["POSITION"] + vertex["NORMAL"])]
                        vertex["TANGENT"] = tangent_var
                    else:
                        tangent_var = vertex["TANGENT"]
                        unique_position_vertices[tuple(vertex["POSITION"] + vertex["NORMAL"])] = tangent_var
                        vertex["TANGENT"] = tangent_var

            indexed_vertex = indexed_vertices.setdefault(HashableVertex(vertex), len(indexed_vertices))
            face.append(indexed_vertex)
        if ib is not None:
            ib.append(face)

    # operator.report({'INFO'}, "Export Vertex Number: " + str(len(indexed_vertices)))
    vb = VertexBuffer(layout=layout)
    for vertex in indexed_vertices:
        vb.append(vertex)

    # Nico: 重计算TANGENT
    if obj.get("3DMigoto:RecalculateTANGENT",False):
        operator.report({'INFO'},"导出时重新计算TANGENT")
        vb.vector_normalized_normal_to_tangent()

    # Nico: 重计算COLOR
    if obj.get("3DMigoto:RecalculateCOLOR",False):
        operator.report({'INFO'},"导出时重新计算COLOR")
        vb.arithmetic_average_normal_to_color()

    # Nico: 写出.fmt .vb .ib文件
    vb.write(open(vb_path, 'wb'), operator=operator)
    ib.write(open(ib_path, 'wb'), operator=operator)
    write_fmt_file(open(fmt_path, 'w'), vb, ib)

    # Force flush make better user experience.
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)



class Export3DMigoto(bpy.types.Operator, ExportHelper):
    """Export a mesh for re-injection into a game with 3DMigoto"""
    bl_idname = "export_mesh.migoto_mmt"
    bl_label = "Export 3DMigoto Vertex & Index Buffers (DBMT)"
    bl_description = "导出当前选中的模型，要求模型必须有3Dmigoto相关属性"

    # file extension
    filename_ext = '.vb'

    # file type filter
    filter_glob: StringProperty(
        default='*.vb',
        options={'HIDDEN'},
    ) # type: ignore

    # 默认选择文件路径
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting",
        subtype='FILE_PATH',
        default="",
    ) # type: ignore

    def execute(self, context):
        try:
            vb_path = self.filepath
            ib_path = os.path.splitext(vb_path)[0] + '.ib'
            fmt_path = os.path.splitext(vb_path)[0] + '.fmt'
            export_3dmigoto(self, context, vb_path, ib_path, fmt_path)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MMTExportAllIBVBModel(bpy.types.Operator):
    bl_idname = "mmt.export_all"
    bl_label = "Export all .ib and .vb model to current OutputFolder"
    bl_description = "一键导出当前集合中所有的模型到对应的DrawIB的文件夹中，命名为从1开始自增的数字"

    def execute(self, context):
        output_folder_path = get_output_folder_path()
        # 遍历当前选中列表的所有mesh，根据名称导出到对应的文件夹中
        # 获取当前选中的对象列表
        selected_collection = bpy.context.collection

        # 遍历选中的对象
        export_time = 0
        for obj in selected_collection.objects:
            # 判断对象是否为网格对象
            if obj.type == 'MESH' and obj.hide_get() == False:
                export_time = export_time + 1
                bpy.context.view_layer.objects.active = obj
                mesh = obj.data  # 获取网格数据

                self.report({'INFO'}, "export name: " + mesh.name)

                # 处理当前网格对象
                # 例如，打印网格名称
                original_name_without_suffix = mesh.name
                if "." in mesh.name: 
                    original_name_without_suffix = str(mesh.name).split(".")[0]
                draw_ib = original_name_without_suffix.split("-")[0]
                draw_index = original_name_without_suffix.split("-")[1]

                # 设置类属性的值
                vb_path = output_folder_path + draw_ib + "\\" + draw_index + ".vb"
                self.report({'INFO'}, "export path: " + vb_path)

                ib_path = os.path.splitext(vb_path)[0] + '.ib'
                fmt_path = os.path.splitext(vb_path)[0] + '.fmt'
                
                export_3dmigoto(self, context, vb_path, ib_path, fmt_path)
        if export_time == 0:
            self.report({'ERROR'}, "导出失败！未导出任何部位！")
        else:
            self.report({'INFO'}, "一键导出成功！成功导出的部位数量：" + str(export_time))
        return {'FINISHED'}
    

class DBMTExportMergedModVBModel(bpy.types.Operator):
    bl_idname = "mmt.export_all_merged"
    bl_label = "Export merged model to current OutputFolder"
    bl_description = "一键导出当前分支架构集合中所有的模型到对应的DrawIB的文件夹中并生成Export.json，隐藏显示的模型不会被导出"

    def execute(self, context):
        output_folder_path = get_output_folder_path()
        # 遍历当前选中列表的所有mesh，根据名称导出到对应的文件夹中
        # 获取当前选中的对象列表
        selected_collection = bpy.context.collection

        draw_ib = selected_collection.name
        if "." in draw_ib:
            draw_ib = draw_ib.split(".")[0]

        # 如果当前集合没有子集合，说明不是一个合格的分支Mod
        if len(selected_collection.children) == 0:
            self.report({'ERROR'},"当前选中集合不是一个标准的分支模型集合，请检查您是否以分支集合方式导入了模型。")
            return {'FINISHED'}
        
        # 构建一个export.json，记录当前集合所有object层级关系
        export_json = {}
        for part_collection in selected_collection.children:
            # 从集合名称中获取导出后部位的名称，如果有.001这种自动添加的后缀则去除掉
            export_part_name = part_collection.name
            if "." in export_part_name:
                export_part_name = export_part_name[0:len(export_part_name) - 4]

            part_collection_json = {}
            for model_collection in part_collection.children:
                # 声明一个model_collection对象
                model_collection_json = {}

                # 先根据颜色确定是什么类型的集合 03是开关 04是分支
                model_collection_type = "default"
                if model_collection.color_tag == "COLOR_03":
                    model_collection_type = "switch"
                elif model_collection.color_tag == "COLOR_04":
                    model_collection_type = "toggle"
                model_collection_json["type"] = model_collection_type

                # 集合中的模型列表
                model_collection_obj_name_list = []
                for obj in model_collection.objects:
                    # 判断对象是否为网格对象，并且不是隐藏状态
                    if obj.type == 'MESH' and obj.hide_get() == False:
                        model_collection_obj_name_list.append("export-" + obj.data.name)
                model_collection_json["model"] = model_collection_obj_name_list

                # 集合的名称后面用作注释标记到ini文件中
                part_collection_json[model_collection.name] = model_collection_json

            export_json[export_part_name] = part_collection_json

        # 将字典转换为 JSON 格式的字符串
        json_string = json.dumps(export_json, ensure_ascii=False, indent=4)
        # 将 JSON 字符串写入文件
        with open(output_folder_path + draw_ib + "\\" + 'export.json', 'w', encoding='utf-8') as f:
            f.write(json_string)

        # 随后直接导出所有模型
        export_time = 0
        for child_part_collection in selected_collection.children:
            for model_collection in child_part_collection.children:
                for obj in model_collection.objects:
                    # 判断对象是否为网格对象
                    if obj.type == 'MESH' and obj.hide_get() == False:
                        bpy.context.view_layer.objects.active = obj
                        vb_path = output_folder_path + draw_ib + "\\" + "export-" + obj.data.name + ".vb"
                        ib_path = os.path.splitext(vb_path)[0] + '.ib'
                        fmt_path = os.path.splitext(vb_path)[0] + '.fmt'
                        
                        export_3dmigoto(self, context, vb_path, ib_path, fmt_path)

                        export_time = export_time + 1

        if export_time == 0:
                self.report({'ERROR'}, "导出失败！请选择一个集合后再点一键导出！")
        else:
            self.report({'INFO'}, "一键导出成功！成功导出的部位数量：" + str(export_time))

            # 调用生成二创模型方法。
            if context.scene.dbmt.generate_mod_after_export:
                result = dbmt_run_generate_mod()
                if result == "success":
                    self.report({'INFO'}, "生成二创模型成功!")
                else:
                    self.report({'ERROR'}, result)
        return {'FINISHED'}
    
