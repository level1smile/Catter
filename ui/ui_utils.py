# Nico: 此文件存放右键菜单所有功能类调用的对应的功能方法
import bpy
import math
import os
import json

from mathutils import Vector


def save_dbmt_path(path):
    # 获取当前脚本文件的路径
    script_path = os.path.abspath(__file__)

    # 获取当前插件的工作目录
    plugin_directory = os.path.dirname(script_path)

    # 构建保存文件的路径
    config_path = os.path.join(plugin_directory, 'Config.json')

    # 创建字典对象
    config = {'dbmt_path': bpy.context.scene.mmt_props.path}

    # 将字典对象转换为 JSON 格式的字符串
    json_data = json.dumps(config)

    # 保存到文件
    with open(config_path, 'w') as file:
        file.write(json_data)


def load_dbmt_path():
    # 获取当前脚本文件的路径
    script_path = os.path.abspath(__file__)

    # 获取当前插件的工作目录
    plugin_directory = os.path.dirname(script_path)

    # 构建配置文件的路径
    config_path = os.path.join(plugin_directory, 'Config.json')

    # 读取文件
    with open(config_path, 'r') as file:
        json_data = file.read()

    # 将 JSON 格式的字符串解析为字典对象
    config = json.loads(json_data)

    # 读取保存的路径
    return config['dbmt_path']


def remove_unused_vertex_group(self, context):
    # Originally design from https://blenderartists.org/t/batch-delete-vertex-groups-script/449881/23
    # Copied from GIMI repository.
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            # obj = bpy.context.active_object
            obj.update_from_editmode()
            vgroup_used = {i: False for i, k in enumerate(obj.vertex_groups)}

            for v in obj.data.vertices:
                for g in v.groups:
                    if g.weight > 0.0:
                        vgroup_used[g.group] = True

            for i, used in sorted(vgroup_used.items(), reverse=True):
                if not used:
                    obj.vertex_groups.remove(obj.vertex_groups[i])

    return {'FINISHED'}


def merge_vertex_group_with_same_number(self, context):
    # Author: SilentNightSound#7430
    # Combines vertex groups with the same prefix into one, a fast alternative to the Vertex Weight Mix that works for multiple groups
    # You will likely want to use blender_fill_vg_gaps.txt after this to fill in any gaps caused by merging groups together
    # Nico: we only need mode 3 here.

    import bpy
    import itertools
    class Fatal(Exception):
        pass

    selected_obj = [obj for obj in bpy.context.selected_objects]
    vgroup_names = []

    ##### USAGE INSTRUCTIONS
    # MODE 1: Runs the merge on a specific list of vertex groups in the selected object(s). Can add more names or fewer to the list - change the names to what you need
    # MODE 2: Runs the merge on a range of vertex groups in the selected object(s). Replace smallest_group_number with the lower bound, and largest_group_number with the upper bound
    # MODE 3 (DEFAULT): Runs the merge on ALL vertex groups in the selected object(s)

    # Select the mode you want to run:
    mode = 3

    # Required data for MODE 1:
    vertex_groups = ["replace_with_first_vertex_group_name", "second_vertex_group_name", "third_name_etc"]

    # Required data for MODE 2:
    smallest_group_number = 000
    largest_group_number = 999

    ######

    if mode == 1:
        vgroup_names = [vertex_groups]
    elif mode == 2:
        vgroup_names = [[f"{i}" for i in range(smallest_group_number, largest_group_number + 1)]]
    elif mode == 3:
        vgroup_names = [[x.name.split(".")[0] for x in y.vertex_groups] for y in selected_obj]
    else:
        raise Fatal("Mode not recognized, exiting")

    if not vgroup_names:
        raise Fatal(
            "No vertex groups found, please double check an object is selected and required data has been entered")

    for cur_obj, cur_vgroup in zip(selected_obj, itertools.cycle(vgroup_names)):
        for vname in cur_vgroup:
            relevant = [x.name for x in cur_obj.vertex_groups if x.name.split(".")[0] == f"{vname}"]

            if relevant:

                vgroup = cur_obj.vertex_groups.new(name=f"x{vname}")

                for vert_id, vert in enumerate(cur_obj.data.vertices):
                    available_groups = [v_group_elem.group for v_group_elem in vert.groups]

                    combined = 0
                    for v in relevant:
                        if cur_obj.vertex_groups[v].index in available_groups:
                            combined += cur_obj.vertex_groups[v].weight(vert_id)

                    if combined > 0:
                        vgroup.add([vert_id], combined, 'ADD')

                for vg in [x for x in cur_obj.vertex_groups if x.name.split(".")[0] == f"{vname}"]:
                    cur_obj.vertex_groups.remove(vg)

                for vg in cur_obj.vertex_groups:
                    if vg.name[0].lower() == "x":
                        vg.name = vg.name[1:]

        bpy.context.view_layer.objects.active = cur_obj
        bpy.ops.object.vertex_group_sort()
    return {'FINISHED'}


def fill_vertex_group_gaps(self, context):
    # Author: SilentNightSound#7430
    # Fills in missing vertex groups for a model so there are no gaps, and sorts to make sure everything is in order
    # Works on the currently selected object
    # e.g. if the selected model has groups 0 1 4 5 7 2 it adds an empty group for 3 and 6 and sorts to make it 0 1 2 3 4 5 6 7
    # Very useful to make sure there are no gaps or out-of-order vertex groups

    # Can change this to another number in order to generate missing groups up to that number
    # e.g. setting this to 130 will create 0,1,2...130 even if the active selected object only has 90
    # Otherwise, it will use the largest found group number and generate everything up to that number
    largest = 0

    ob = bpy.context.active_object
    ob.update_from_editmode()

    for vg in ob.vertex_groups:
        try:
            if int(vg.name.split(".")[0]) > largest:
                largest = int(vg.name.split(".")[0])
        except ValueError:
            print("Vertex group not named as integer, skipping")

    missing = set([f"{i}" for i in range(largest + 1)]) - set([x.name.split(".")[0] for x in ob.vertex_groups])
    for number in missing:
        ob.vertex_groups.new(name=f"{number}")

    bpy.ops.object.vertex_group_sort()
    return {'FINISHED'}


def add_bone_from_vertex_group(self, context):
    # 获取当前选中的物体
    selected_object = bpy.context.object

    # 创建骨骼
    bpy.ops.object.armature_add()
    armature_object = bpy.context.object
    armature = armature_object.data

    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    # 遍历所有的顶点组
    for vertex_group in selected_object.vertex_groups:
        # 获取顶点组的名称
        vertex_group_name = vertex_group.name

        # 创建骨骼
        bone = armature.edit_bones.new(vertex_group_name)

        # 根据顶点组位置生成骨骼
        for vertex in selected_object.data.vertices:
            for group_element in vertex.groups:
                if group_element.group == vertex_group.index:
                    # 获取顶点位置
                    vertex_position = selected_object.matrix_world @ vertex.co

                    # 设置骨骼位置
                    bone.head = vertex_position
                    bone.tail = Vector(vertex_position) + Vector((0, 0, 0.1))  # 设置骨骼长度

                    # 分配顶点到骨骼
                    bone_vertex_group = selected_object.vertex_groups[vertex_group_name]
                    bone_vertex_group.add([vertex.index], 0, 'ADD')

    # 刷新场景
    bpy.context.view_layer.update()

    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')

    # 选择骨骼并绑定物体到骨骼
    # bpy.context.view_layer.objects.active = armature_object  # 激活骨骼
    # bpy.ops.object.select_all(action='DESELECT')  # 取消选择所有
    # selected_object.select_set(True)  # 选择物体
    # bpy.ops.object.parent_set(type='ARMATURE_AUTO')  # 绑定物体到骨骼

    # 刷新场景
    bpy.context.view_layer.update()

    return {'FINISHED'}


def remove_not_number_vertex_group(self, context):
    for obj in bpy.context.selected_objects:
        for vg in reversed(obj.vertex_groups):
            if vg.name.isdecimal():
                continue
            # print('Removing vertex group', vg.name)
            obj.vertex_groups.remove(vg)
    return {'FINISHED'}


def convert_to_fragment(self, context):
    # 获取当前选中的对象
    selected_objects = bpy.context.selected_objects

    # 检查是否选中了一个Mesh对象
    if len(selected_objects) != 1 or selected_objects[0].type != 'MESH':
        raise ValueError("请选中一个Mesh对象")

    # 获取选中的网格对象
    mesh_obj = selected_objects[0]
    mesh = mesh_obj.data

    # 遍历所有面
    selected_face_index = -1
    for i, face in enumerate(mesh.polygons):
        # 检查当前面是否已经是一个三角形
        if len(face.vertices) == 3:
            selected_face_index = i
            break

    if selected_face_index == -1:
        raise ValueError("没有选中的三角形面")

    # 选择指定索引的面
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    # 选择指定面的所有顶点
    bpy.context.tool_settings.mesh_select_mode[0] = True
    bpy.context.tool_settings.mesh_select_mode[1] = False
    bpy.context.tool_settings.mesh_select_mode[2] = False

    bpy.ops.object.mode_set(mode='OBJECT')

    # 获取选中面的所有顶点索引
    selected_face = mesh.polygons[selected_face_index]
    selected_vertices = [v for v in selected_face.vertices]

    # 删除非选定面的顶点
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.context.tool_settings.mesh_select_mode[0] = True
    bpy.context.tool_settings.mesh_select_mode[1] = False
    bpy.context.tool_settings.mesh_select_mode[2] = False

    bpy.ops.object.mode_set(mode='OBJECT')

    for vertex in mesh.vertices:
        if vertex.index not in selected_vertices:
            vertex.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')

    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')

    # 更新网格数据
    mesh_obj.data.update()

    return {'FINISHED'}


def delete_loose(self, context):
    # 获取当前选中的对象
    selected_objects = bpy.context.selected_objects
    # 检查是否选中了一个Mesh对象
    for obj in selected_objects:
        if obj.type == 'MESH':
            # 获取选中的网格对象
            bpy.ops.object.mode_set(mode='EDIT')
            # 选择所有的顶点
            bpy.ops.mesh.select_all(action='SELECT')
            # 执行删除孤立顶点操作
            bpy.ops.mesh.delete_loose()
            # 切换回对象模式
            bpy.ops.object.mode_set(mode='OBJECT')
    return {'FINISHED'}


def mmt_reset_rotation(self, context):
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            # 将旋转角度归零
            obj.rotation_euler[0] = 0.0  # X轴
            obj.rotation_euler[1] = 0.0  # Y轴
            obj.rotation_euler[2] = 0.0  # Z轴

            # 应用旋转变换
            # bpy.context.view_layer.objects.active = obj
            # bpy.ops.object.transform_apply(rotation=True)
    return {'FINISHED'}


def split_mesh_by_common_vertex_group(self, context):
    # Code copied and modified from @Kail_Nethunter, very useful in some special meets.
    # https://blenderartists.org/t/split-a-mesh-by-vertex-groups/438990/11

    for obj in bpy.context.selected_objects:
        origin_name = obj.name
        keys = obj.vertex_groups.keys()
        real_keys = []
        for gr in keys:
            bpy.ops.object.mode_set(mode="EDIT")
            # Set the vertex group as active
            bpy.ops.object.vertex_group_set_active(group=gr)

            # Deselect all verts and select only current VG
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.vertex_group_select()
            # bpy.ops.mesh.select_all(action='INVERT')
            try:
                bpy.ops.mesh.separate(type="SELECTED")
                real_keys.append(gr)
            except:
                pass
        for i in range(1, len(real_keys) + 1):
            bpy.data.objects['{}.{:03d}'.format(origin_name, i)].name = '{}.{}'.format(
                origin_name, real_keys[i - 1])

    return {'FINISHED'}



