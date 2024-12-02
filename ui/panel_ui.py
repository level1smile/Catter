import bpy
import os
import json

from ..utils.migoto_utils import *
from ..utils.vertexgroup_utils import *
from ..utils.dbmt_utils import *
from ..migoto.migoto_format import InputLayout

class CatterConfigUI(bpy.types.Panel):
    bl_label = "基础配置"
    bl_idname = "CATTER_PT_CONFIG_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        # Path button to choose DBMT-GUI.exe location folder.
        layout.prop(context.scene.dbmt,"path")

        # 获取DBMT.exe的路径
        dbmt_gui_exe_path = os.path.join(context.scene.dbmt.path, "DBMT-GUI.exe")
        if not os.path.exists(dbmt_gui_exe_path):
            layout.label(text="错误:请选择DBMT-GUI.exe所在路径 ", icon='ERROR')
        
        row = layout.row()
        row.label(text="当前游戏: " + get_current_game_from_main_json())

        layout.separator(type="LINE")


        layout.label(text="翻转NORMAL分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_normal_x", text="X")
        row.prop(context.scene.dbmt, "flip_normal_y", text="Y")
        row.prop(context.scene.dbmt, "flip_normal_z", text="Z")
        row.prop(context.scene.dbmt, "flip_normal_w", text="W")

        layout.separator(type="LINE")

        layout.label(text="翻转TANGENT分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_tangent_x", text="X")
        row.prop(context.scene.dbmt, "flip_tangent_y", text="Y")
        row.prop(context.scene.dbmt, "flip_tangent_z", text="Z")
        row.prop(context.scene.dbmt, "flip_tangent_w", text="W")

        layout.separator(type="LINE")
        layout.prop(context.scene.dbmt, "export_same_number", text="导出不改变顶点数")
        layout.prop(context.scene.dbmt,"generate_mod_after_export",text="一键导出后自动生成二创模型")
        layout.prop(context.scene.dbmt,"import_merged_vgmap",text="使用重映射的全局顶点组")


class MigotoIOPanel(bpy.types.Panel):
    bl_label = "导入/导出" 
    bl_idname = "VIEW3D_PT_CATTER_IO_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        # Get output folder path.
        output_folder_path = get_output_folder_path()

        # 分隔符
        layout.label(text="在OutputFolder中导入或导出")

        # 手动导入buf文件
        operator_import_ib_vb = self.layout.operator("import_mesh.migoto_raw_buffers_mmt", text="导入 .ib & .vb 模型文件")
        operator_import_ib_vb.filepath = output_folder_path

        # 手动导出同理，点这个之后默认路径为OutputFolder，这样直接就能去导出不用翻很久文件夹找路径了
        operator_export_ibvb = self.layout.operator("export_mesh.migoto_mmt", text="导出 .ib & .vb 模型文件")
        operator_export_ibvb.filepath = output_folder_path + "1.vb"

        current_game = get_current_game_from_main_json()
        # hoyogames use new architecture so can't use old import export method.
        if current_game not in ["HI3","GI","HSR","ZZZ","Unity-CPU-PreSkinning","Game001","LiarsBar","BloodySpell"]:
            # 添加分隔符
            layout.separator(type="LINE")
            layout.label(text="该游戏支持仍在测试中", icon='ERROR')
            # 一键快速导入
            layout.label(text="在OutputFolder中一键导入导出")
            operator_fast_import = self.layout.operator("mmt.import_all", text="一键导入所有模型文件")

            # 一键快速导出当前选中Collection中的所有model到对应的hash值文件夹中
            # TODO 直接调用MMT.exe的Mod生成方法，做到导出完即可游戏里F10刷新看效果。
            operator_export_ibvb = self.layout.operator("mmt.export_all", text="一键导出选中的集合")
        else:
            # 添加分隔符
            layout.separator(type="LINE")
            layout.label(text="导入导出模型集合(支持分支)")

            # mmt.import_all_merged
            operator_fast_import_merged = self.layout.operator("mmt.import_all_merged", text="一键导入所有模型文件")
            operator_export_ibvb_merged = self.layout.operator("mmt.export_all_merged", text="一键导出选中的集合")



class MigotoAttributePanel(bpy.types.Panel):
    bl_label = "3Dmigoto属性" 
    bl_idname = "VIEW3D_PT_CATTER_MigotoAttribute_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout
        # 检查是否有选中的对象
        if len(context.selected_objects) > 0:
            # 获取第一个选中的对象
            selected_obj = context.selected_objects[0]
            
            # 显示对象名称
            row = layout.row()
            row.label(text=f"当前Object名称: {selected_obj.name}")
            row = layout.row()
            row.label(text=f"对象Data名称: {selected_obj.data.name}")

            layout.separator(type="LINE")

            # 示例：显示位置信息
            recalculate_tangent = selected_obj.get("3DMigoto:RecalculateTANGENT",None)
            if recalculate_tangent is not None:
                row = layout.row()
                row.label(text=f"导出时重计算TANGENT:" + str(recalculate_tangent))

            recalculate_color = selected_obj.get("3DMigoto:RecalculateCOLOR",None)
            if recalculate_color is not None:
                row = layout.row()
                row.label(text=f"导出时重计算COLOR:" + str(recalculate_color))

            layout.separator(type="LINE")

            vblayout = selected_obj.get("3DMigoto:VBLayout",None)
            if vblayout is not None:
                for element_property in vblayout:
                    row = layout.row()
                    semantic_index_suffix = ""
                    if element_property["SemanticIndex"] != 0:
                        semantic_index_suffix = str(element_property["SemanticIndex"])
                    row.label(text=element_property["SemanticName"] + semantic_index_suffix +"        " + element_property["Format"] )

            vbstride = selected_obj.get("3DMigoto:VBStride",None)
            if vbstride is not None:
                row = layout.row()
                row.label(text=f"3DMigoto:VBStride: " + str(vbstride))

            firstvertex = selected_obj.get("3DMigoto:FirstVertex",None)
            if firstvertex is not None:
                row = layout.row()
                row.label(text=f"3DMigoto:FirstVertex: " + str(firstvertex))

            ibformat = selected_obj.get("3DMigoto:IBFormat",None)
            if ibformat is not None:
                row = layout.row()
                row.label(text=f"3DMigoto:IBFormat: " + str(ibformat))

            firstindex = selected_obj.get("3DMigoto:FirstIndex",None)
            if firstindex is not None:
                row = layout.row()
                row.label(text=f"3DMigoto:FirstIndex: " + str(firstindex))
            
        else:
            # 如果没有选中的对象，则显示提示信息
            row = layout.row()
            row.label(text="未选中mesh对象")

