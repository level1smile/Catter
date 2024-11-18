# Nico: 此文件定义右键菜单的功能类。
# 4.2版本开始，bl_options里再加任何东西都会出现 
# RuntimeError: Error: validating class:: 'REGISTER' not found in ('SEARCH_ON_KEY_PRESS')
from .mesh_functions import *


class RemoveUnusedVertexGroupOperator(bpy.types.Operator):
    bl_idname = "object.remove_unused_vertex_group"
    bl_label = "移除未使用的空顶点组"

    def execute(self, context):
        return remove_unused_vertex_group(self, context)


class MergeVertexGroupsWithSameNumber(bpy.types.Operator):
    bl_idname = "object.merge_vertex_group_with_same_number"
    bl_label = "合并具有相同数字前缀名称的顶点组"
    
    def execute(self, context):
        return merge_vertex_group_with_same_number(self, context)


class FillVertexGroupGaps(bpy.types.Operator):
    bl_idname = "object.fill_vertex_group_gaps"
    bl_label = "填充数字顶点组的间隙"
    
    def execute(self, context):
        return fill_vertex_group_gaps(self, context)


class AddBoneFromVertexGroup(bpy.types.Operator):
    bl_idname = "object.add_bone_from_vertex_group"
    bl_label = "根据顶点组自动生成骨骼"
    
    def execute(self, context):
        return add_bone_from_vertex_group(self, context)


class RemoveNotNumberVertexGroup(bpy.types.Operator):
    bl_idname = "object.remove_not_number_vertex_group"
    bl_label = "移除非数字名称的顶点组"
    
    def execute(self, context):
        return remove_not_number_vertex_group(self, context)


class ConvertToFragmentOperator(bpy.types.Operator):
    bl_idname = "object.convert_to_fragment"
    bl_label = "转换为一个3Dmigoto碎片用于合并"
    
    def execute(self, context):
        return convert_to_fragment(self, context)


class MMTDeleteLoose(bpy.types.Operator):
    bl_idname = "object.mmt_delete_loose"
    bl_label = "删除物体的松散点"
    
    def execute(self, context):
        return delete_loose(self, context)


class MMTResetRotation(bpy.types.Operator):
    bl_idname = "object.mmt_reset_rotation"
    bl_label = "重置x,y,z的旋转角度为0 (UE Model)"
    
    def execute(self, context):
        return mmt_reset_rotation(self, context)



class SplitMeshByCommonVertexGroup(bpy.types.Operator):
    bl_idname = "object.split_mesh_by_common_vertex_group"
    bl_label = "根据相同的顶点组分割物体"
    
    def execute(self, context):
        return split_mesh_by_common_vertex_group(self, context)


class RecalculateTANGENTWithVectorNormalizedNormal(bpy.types.Operator):
    bl_idname = "object.recalculate_tangent_arithmetic_average_normal"
    bl_label = "使用向量相加归一化算法重计算TANGENT"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.get("3DMigoto:RecalculateTANGENT",False):
                    obj["3DMigoto:RecalculateTANGENT"] = not obj["3DMigoto:RecalculateTANGENT"]
                else:
                    obj["3DMigoto:RecalculateTANGENT"] = True
                self.report({'INFO'},"重计算TANGENT设为:" + str(obj["3DMigoto:RecalculateTANGENT"]))
        return {'FINISHED'}


class RecalculateCOLORWithVectorNormalizedNormal(bpy.types.Operator):
    bl_idname = "object.recalculate_color_arithmetic_average_normal"
    bl_label = "使用算术平均归一化算法重计算COLOR"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.get("3DMigoto:RecalculateCOLOR",False):
                    obj["3DMigoto:RecalculateCOLOR"] = not obj["3DMigoto:RecalculateCOLOR"]
                else:
                    obj["3DMigoto:RecalculateCOLOR"] = True
                self.report({'INFO'},"重计算COLOR设为:" + str(obj["3DMigoto:RecalculateCOLOR"]))
        return {'FINISHED'}

 
# -----------------------------------这个属于右键菜单注册，单独的函数要往上面放---------------------------------------
class MigotoRightClickMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_object_3Dmigoto"
    bl_label = "3Dmigoto"
    
    def draw(self, context):
        layout = self.layout
        # layout.operator可以直接用 [类名.bl_idname] 这样就不用再写一次常量了，方便管理
        layout.operator(RemoveUnusedVertexGroupOperator.bl_idname)
        layout.operator(MergeVertexGroupsWithSameNumber.bl_idname)
        layout.operator(FillVertexGroupGaps.bl_idname)
        layout.operator(AddBoneFromVertexGroup.bl_idname)
        layout.operator(RemoveNotNumberVertexGroup.bl_idname)
        layout.operator(ConvertToFragmentOperator.bl_idname)
        layout.operator(MMTDeleteLoose.bl_idname)
        layout.operator(MMTResetRotation.bl_idname)
        layout.operator(SplitMeshByCommonVertexGroup.bl_idname)
        layout.separator()
        layout.operator(RecalculateTANGENTWithVectorNormalizedNormal.bl_idname)
        layout.operator(RecalculateCOLORWithVectorNormalizedNormal.bl_idname)


# 定义菜单项的注册函数
def menu_func_migoto_right_click(self, context):
    self.layout.menu(MigotoRightClickMenu.bl_idname)


# --------------------------
# Right click menu for collection.
class DBMT_MarkCollection_Switch(bpy.types.Operator):
    # bl_idname必须小写，中间可以下划线分割，不然报错无法加载
    bl_idname = "object.mark_collection_switch"
    bl_label = "Mark Collection Switch"

    def execute(self, context):
        # 示例：打印当前选中的集合名称
        if context.collection:
            context.collection.color_tag = "COLOR_03"
        return {'FINISHED'}


class DBMT_MarkCollection_Toggle(bpy.types.Operator):
    # bl_idname必须小写，中间可以下划线分割，不然报错无法加载
    bl_idname = "object.mark_collection_toggle"
    bl_label = "Mark Collection Toggle"

    def execute(self, context):
        # 示例：打印当前选中的集合名称
        if context.collection:
            context.collection.color_tag = "COLOR_04"
        return {'FINISHED'}


def menu_dbmt_mark_collection_switch(self, context):
    self.layout.separator()
    self.layout.operator(DBMT_MarkCollection_Switch.bl_idname, text="分支:标记为按键开关类型")
    self.layout.operator(DBMT_MarkCollection_Toggle.bl_idname, text="分支:标记为按键切换类型")