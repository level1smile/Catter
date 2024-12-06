import bpy
import os
import json

from ..utils.migoto_utils import *
from ..utils.vertexgroup_utils import *
from ..utils.dbmt_utils import *
from ..migoto.input_layout import InputLayout

class CatterConfigUI(bpy.types.Panel):
    bl_label = "基础配置"
    bl_idname = "CATTER_PT_CONFIG_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="DBMT-GUI.exe所在路径")

        # Path button to choose DBMT-GUI.exe location folder.
        row = layout.row()
        row.prop(context.scene.dbmt,"path",text="")

        layout.separator(type="LINE")

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


class PanelModelImport(bpy.types.Panel):
    bl_label = "模型导入" 
    bl_idname = "VIEW3D_PT_CATTER_ModelImport_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.dbmt, "workspace_namelist")
        
        operator_import_ib_vb = layout.operator("import_mesh.migoto_raw_buffers_mmt", text="导入 .ib & .vb 模型文件")
        operator_import_ib_vb.filepath = dbmt_get_workspaced_output_folder_path()
        layout.operator("mmt.import_all_merged", text="一键导入所有模型到工作空间集合[分支架构]")


class PanelModelExport(bpy.types.Panel):
    bl_label = "模型导出" 
    bl_idname = "VIEW3D_PT_CATTER_IO_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.dbmt, "workspace_namelist")


        # 手动导出同理，点这个之后默认路径为OutputFolder，这样直接就能去导出不用翻很久文件夹找路径了
        operator_export_ibvb = layout.operator("export_mesh.migoto_mmt", text="导出 .ib & .vb 模型文件")
        operator_export_ibvb.filepath = dbmt_get_workspaced_output_folder_path() + "1.vb"

        layout.operator("mmt.export_all_merged", text="一键导出选中的工作空间集合[分支架构]")


class PanelModelExtract(bpy.types.Panel):
    bl_label = "FrameAnalysis模型提取" 
    bl_idname = "VIEW3D_PT_CATTER_ModelExtract_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="提取出的模型文件默认存储路径")
        row = layout.row()
        row.prop(context.scene.dbmt,"model_extract_output_path",text="")
        layout.separator(type="LINE")

        layout.row().label(text="工作空间名称")
        row = layout.row()
        row.prop(context.scene.dbmt,"model_workspace_name")
        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="DrawIB列表")
        row = layout.row()
        row.prop(context.scene.dbmt,"draw_ib_input_text")
        layout.separator(type="LINE")



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
            layout.row().label(text=f"当前Object名称: {selected_obj.name}")
            layout.row().label(text=f"对象Data名称: {selected_obj.data.name}")
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


            gametypename = selected_obj.get("3DMigoto:GameTypeName",None)
            if gametypename is not None:
                row = layout.row()
                row.label(text=f"GameType: " + str(gametypename))

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

