from ..utils.vertexgroup_utils import *
from ..utils.shapekey_utils import *
from ..utils.mesh_utils import *

from bpy.props import BoolProperty,  CollectionProperty


class RemoveAllVertexGroupOperator(bpy.types.Operator):
    bl_idname = "object.remove_all_vertex_group"
    bl_label = "移除所有顶点组"
    bl_description = "移除当前选中obj的所有顶点组"

    def execute(self, context):
        return remove_all_vertex_groups(self,context)

class RemoveUnusedVertexGroupOperator(bpy.types.Operator):
    bl_idname = "object.remove_unused_vertex_group"
    bl_label = "移除未使用的空顶点组"
    bl_description = "移除当前选中obj的所有空顶点组，也就是移除未使用的顶点组"

    def execute(self, context):
        return remove_unused_vertex_group(self, context)


class MergeVertexGroupsWithSameNumber(bpy.types.Operator):
    bl_idname = "object.merge_vertex_group_with_same_number"
    bl_label = "合并具有相同数字前缀名称的顶点组"
    bl_description = "把当前选中obj的所有数字前缀名称相同的顶点组进行合并"

    def execute(self, context):
        return merge_vertex_group_with_same_number(self, context)


class FillVertexGroupGaps(bpy.types.Operator):
    bl_idname = "object.fill_vertex_group_gaps"
    bl_label = "填充数字顶点组的间隙"
    bl_description = "把当前选中obj的所有数字顶点组的间隙用数字命名的空顶点组填补上，比如有顶点组1,2,5,8则填补后得到1,2,3,4,5,6,7,8"

    def execute(self, context):
        return fill_vertex_group_gaps(self, context)


class AddBoneFromVertexGroup(bpy.types.Operator):
    bl_idname = "object.add_bone_from_vertex_group"
    bl_label = "根据顶点组自动生成骨骼"
    bl_description = "把当前选中的obj的每个顶点组都生成一个默认位置的骨骼，方便接下来手动调整骨骼位置和父级关系来绑骨"
    def execute(self, context):
        return add_bone_from_vertex_group(self, context)


class RemoveNotNumberVertexGroup(bpy.types.Operator):
    bl_idname = "object.remove_not_number_vertex_group"
    bl_label = "移除非数字名称的顶点组"
    bl_description = "把当前选中的obj的所有不是纯数字命名的顶点组都移除"

    def execute(self, context):
        return remove_not_number_vertex_group(self, context)


class ConvertToFragmentOperator(bpy.types.Operator):
    bl_idname = "object.convert_to_fragment"
    bl_label = "转换为一个3Dmigoto碎片用于合并"
    bl_description = "把当前选中的obj删除到只剩一个随机的三角面，用于合并到此三角面上使模型获取此obj的属性"
    
    def execute(self, context):
        return convert_to_fragment(self, context)


class MMTDeleteLoose(bpy.types.Operator):
    bl_idname = "object.mmt_delete_loose"
    bl_label = "删除物体的松散点"
    bl_description = "把当前选中的obj的所有松散点都删除"
    
    def execute(self, context):
        return delete_loose(self, context)


class MMTResetRotation(bpy.types.Operator):
    bl_idname = "object.mmt_reset_rotation"
    bl_label = "重置x,y,z的旋转角度为0 (UE Model)"
    bl_description = "把当前选中的obj的x,y,z的旋转角度全部归0"
    
    def execute(self, context):
        return mmt_reset_rotation(self, context)



class SplitMeshByCommonVertexGroup(bpy.types.Operator):
    bl_idname = "object.split_mesh_by_common_vertex_group"
    bl_label = "根据相同的顶点组分割物体"
    bl_description = "把当前选中的obj按顶点组进行分割，适用于部分精细刷权重并重新组合模型的场景"
    
    def execute(self, context):
        return split_mesh_by_common_vertex_group(self, context)


class RecalculateTANGENTWithVectorNormalizedNormal(bpy.types.Operator):
    bl_idname = "object.recalculate_tangent_arithmetic_average_normal"
    bl_label = "使用向量相加归一化算法重计算TANGENT"
    bl_description = "近似修复轮廓线算法，可以达到99%的轮廓线相似度，适用于GI,HSR,ZZZ,HI3 2.0之前的老角色" 
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
    bl_description = "近似修复轮廓线算法，可以达到99%的轮廓线相似度，仅适用于HI3 2.0新角色" 

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.get("3DMigoto:RecalculateCOLOR",False):
                    obj["3DMigoto:RecalculateCOLOR"] = not obj["3DMigoto:RecalculateCOLOR"]
                else:
                    obj["3DMigoto:RecalculateCOLOR"] = True
                self.report({'INFO'},"重计算COLOR设为:" + str(obj["3DMigoto:RecalculateCOLOR"]))
        return {'FINISHED'}




class PropertyCollectionModifierItem(bpy.types.PropertyGroup):
    # Code originally copied from WWMI to avoid make another wheel again and modified to better meet our needs.
    # https://github.com/SpectrumQT/WWMI-TOOLS
    # Credit to SpectrumQT and huge thanks for his hard work.
    checked: BoolProperty(
        name="", 
        default=False
    ) # type: ignore
bpy.utils.register_class(PropertyCollectionModifierItem)

class WWMI_ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    # Code originally copied from WWMI to avoid make another wheel again and modified to better meet our needs.
    # https://github.com/SpectrumQT/WWMI-TOOLS
    # Credit to SpectrumQT and huge thanks for his hard work.
    bl_idname = "wwmi_tools.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply Modifiers For Object With Shape Keys"
    bl_description = "Apply selected modifiers and remove from the stack for object with shape keys (Solves 'Modifier cannot be applied to a mesh with shape keys' error when pushing 'Apply' button in 'Object modifiers'). Sourced by Przemysław Bągard"
 
    def item_list(self, context):
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.object.modifiers]
    
    my_collection: CollectionProperty(
        type=PropertyCollectionModifierItem
    ) # type: ignore
    
    disable_armatures: BoolProperty(
        name="Don't include armature deformations",
        default=True,
    ) # type: ignore
 
    def execute(self, context):
        ob = bpy.context.object
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = ob
        ob.select_set(True)
        
        selectedModifiers = [o.name for o in self.my_collection if o.checked]
        
        if not selectedModifiers:
            self.report({'ERROR'}, 'No modifier selected!')
            return {'FINISHED'}
        
        success, errorInfo = apply_modifiers_for_object_with_shape_keys(context, selectedModifiers, self.disable_armatures)
        
        if not success:
            self.report({'ERROR'}, errorInfo)
        
        return {'FINISHED'}
        
    def draw(self, context):
        if context.object.data.shape_keys and context.object.data.shape_keys.animation_data:
            self.layout.separator()
            self.layout.label(text="Warning:")
            self.layout.label(text="              Object contains animation data")
            self.layout.label(text="              (like drivers, keyframes etc.)")
            self.layout.label(text="              assigned to shape keys.")
            self.layout.label(text="              Those data will be lost!")
            self.layout.separator()
        #self.layout.prop(self, "my_enum")
        box = self.layout.box()
        for prop in self.my_collection:
            box.prop(prop, "checked", text=prop["name"])
        #box.prop(self, "my_collection")
        self.layout.prop(self, "disable_armatures")
 
    def invoke(self, context, event):
        self.my_collection.clear()
        for i in range(len(bpy.context.object.modifiers)):
            item = self.my_collection.add()
            item.name = bpy.context.object.modifiers[i].name
            item.checked = False
        return context.window_manager.invoke_props_dialog(self)
 
 
class CatterRightClickMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_object_3Dmigoto"
    bl_label = "3Dmigoto"
    bl_description = "适用于3Dmigoto Mod制作的常用功能"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(RemoveAllVertexGroupOperator.bl_idname)
        layout.operator(RemoveUnusedVertexGroupOperator.bl_idname)
        layout.operator(MergeVertexGroupsWithSameNumber.bl_idname)
        layout.operator(FillVertexGroupGaps.bl_idname)
        layout.operator(AddBoneFromVertexGroup.bl_idname)
        layout.operator(RemoveNotNumberVertexGroup.bl_idname)
        layout.operator(ConvertToFragmentOperator.bl_idname)
        layout.operator(MMTDeleteLoose.bl_idname)
        layout.operator(MMTResetRotation.bl_idname)
        layout.operator(SplitMeshByCommonVertexGroup.bl_idname)
        layout.operator(WWMI_ApplyModifierForObjectWithShapeKeysOperator.bl_idname)
        layout.separator()
        layout.operator(RecalculateTANGENTWithVectorNormalizedNormal.bl_idname)
        layout.operator(RecalculateCOLORWithVectorNormalizedNormal.bl_idname)
        


def menu_func_migoto_right_click(self, context):
    self.layout.separator()
    self.layout.menu(CatterRightClickMenu.bl_idname)


class Catter_MarkCollection_Switch(bpy.types.Operator):
    bl_idname = "object.mark_collection_switch"
    bl_label = "分支:标记为按键切换类型"
    bl_description = "把当前选中集合标记为按键切换分支集合"

    def execute(self, context):
        if context.collection:
            context.collection.color_tag = "COLOR_03"
        return {'FINISHED'}


class Catter_MarkCollection_Toggle(bpy.types.Operator):
    bl_idname = "object.mark_collection_toggle"
    bl_label = "分支:标记为按键开关类型"
    bl_description = "把当前选中集合标记为按键开关分支集合"

    def execute(self, context):
        if context.collection:
            context.collection.color_tag = "COLOR_04"
        return {'FINISHED'}


def menu_dbmt_mark_collection_switch(self, context):
    self.layout.separator()
    self.layout.operator(Catter_MarkCollection_Switch.bl_idname, text="分支:标记为按键开关类型")
    self.layout.operator(Catter_MarkCollection_Toggle.bl_idname, text="分支:标记为按键切换类型")