
import bpy

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

