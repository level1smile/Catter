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

        draw_seperator(self)

        # 获取DBMT.exe的路径
        dbmt_gui_exe_path = os.path.join(context.scene.dbmt.path, "DBMT-GUI.exe")
        if not os.path.exists(dbmt_gui_exe_path):
            layout.label(text="错误:请选择DBMT-GUI.exe所在路径 ", icon='ERROR')
        
        row = layout.row()
        row.label(text="当前游戏: " + get_current_game_from_main_json())

        draw_seperator(self)


        layout.label(text="翻转NORMAL分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_normal_x", text="X")
        row.prop(context.scene.dbmt, "flip_normal_y", text="Y")
        row.prop(context.scene.dbmt, "flip_normal_z", text="Z")
        row.prop(context.scene.dbmt, "flip_normal_w", text="W")

        draw_seperator(self)

        layout.label(text="翻转TANGENT分量")
        row = layout.row()
       
        row.prop(context.scene.dbmt, "flip_tangent_x", text="X")
        row.prop(context.scene.dbmt, "flip_tangent_y", text="Y")
        row.prop(context.scene.dbmt, "flip_tangent_z", text="Z")
        row.prop(context.scene.dbmt, "flip_tangent_w", text="W")

        draw_seperator(self)
        layout.prop(context.scene.dbmt, "export_same_number", text="导出不改变顶点数")
      
        layout.prop(context.scene.dbmt,"import_merged_vgmap",text="使用重映射的全局顶点组")
        layout.prop(context.scene.dbmt,"model_scale")
        


class PanelModelSingleIO(bpy.types.Panel):
    bl_label = "模型手动导入导出" 
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
        # 手动导出同理，点这个之后默认路径为OutputFolder，这样直接就能去导出不用翻很久文件夹找路径了
        operator_export_ibvb = layout.operator("export_mesh.migoto_mmt", text="导出 .ib & .vb 模型文件")
        operator_export_ibvb.filepath = dbmt_get_workspaced_output_folder_path() + "1.vb"



class PanelModelFastIO(bpy.types.Panel):
    bl_label = "从选择的工作空间中导入导出" 
    bl_idname = "VIEW3D_PT_CATTER_IO_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.dbmt, "workspace_namelist")

        layout.operator("mmt.import_all_merged", text="一键导入所有模型到工作空间集合[分支架构]")

        draw_seperator(self)
        layout.prop(context.scene.dbmt,"generate_mod_after_export",text="一键导出后自动生成二创模型")
        layout.operator("mmt.export_all_merged", text="一键导出选中的工作空间集合[分支架构]")

class PanelModelWorkSpaceIO(bpy.types.Panel):
    bl_label = "从当前工作空间中导入导出" 
    bl_idname = "VIEW3D_PT_CATTER_WorkSpace_IO_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="当前工作空间: " + get_current_workspacename_from_main_json())

        # TODO 这俩要抽象出单独一个导入导出的，再由不同接口调用。
        layout.operator("dbmt.import_all_from_workspace", text="一键导入")

        draw_seperator(self)
        layout.prop(context.scene.dbmt,"generate_mod_after_export",text="一键导出后自动生成二创模型")
        layout.operator("dbmt.export_all_to_workspace", text="一键导出")


class PanelGenerateMod(bpy.types.Panel):
    bl_label = "Generate Mod" 
    bl_idname = "VIEW3D_PT_CATTER_GenerateMod_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Author Name:")
        layout.prop(context.scene.dbmt, "credit_info_author_name")
        layout.label(text="Social Link:")
        layout.prop(context.scene.dbmt, "credit_info_author_social_link")


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
            draw_seperator(self)

            # 示例：显示位置信息
            recalculate_tangent = selected_obj.get("3DMigoto:RecalculateTANGENT",None)
            if recalculate_tangent is not None:
                row = layout.row()
                row.label(text=f"导出时重计算TANGENT:" + str(recalculate_tangent))

            recalculate_color = selected_obj.get("3DMigoto:RecalculateCOLOR",None)
            if recalculate_color is not None:
                row = layout.row()
                row.label(text=f"导出时重计算COLOR:" + str(recalculate_color))

            draw_seperator(self)


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

