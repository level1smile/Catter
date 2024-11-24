import bpy
import os
import json

from ..migoto.migoto_utils import *
from .ui_utils import *



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

        layout.prop(context.scene.dbmt, "export_same_number", text="导出不改变顶点数")


        layout.label(text="翻转NORMAL分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_normal_x", text="X")
        row.prop(context.scene.dbmt, "flip_normal_y", text="Y")
        row.prop(context.scene.dbmt, "flip_normal_z", text="Z")
        row.prop(context.scene.dbmt, "flip_normal_w", text="W")

        layout.label(text="翻转TANGENT分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_tangent_x", text="X")
        row.prop(context.scene.dbmt, "flip_tangent_y", text="Y")
        row.prop(context.scene.dbmt, "flip_tangent_z", text="Z")
        row.prop(context.scene.dbmt, "flip_tangent_w", text="W")


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
        if current_game not in ["HI3","GI","HSR","ZZZ","Unity-CPU-PreSkinning","Game001"]:
            # 添加分隔符
            layout.separator()
            layout.label(text="该游戏支持仍在测试中", icon='ERROR')
            # 一键快速导入
            layout.label(text="在OutputFolder中一键导入导出")
            operator_fast_import = self.layout.operator("mmt.import_all", text="一键导入所有模型文件")

            # 一键快速导出当前选中Collection中的所有model到对应的hash值文件夹中
            # TODO 直接调用MMT.exe的Mod生成方法，做到导出完即可游戏里F10刷新看效果。
            operator_export_ibvb = self.layout.operator("mmt.export_all", text="一键导出选中的集合")
        else:
            # 添加分隔符
            layout.separator()
            layout.label(text="导入导出模型集合(支持分支)")

            # mmt.import_all_merged
            operator_fast_import_merged = self.layout.operator("mmt.import_all_merged", text="一键导入所有模型文件")
            operator_export_ibvb_merged = self.layout.operator("mmt.export_all_merged", text="一键导出选中的集合")



