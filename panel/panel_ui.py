import bpy

from .panel_functions import *
from ..migoto.migoto_utils import *

class CatterConfigUI(bpy.types.Panel):
    bl_label = "Config"
    bl_idname = "CATTER_PT_CONFIG_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        # Path button to choose DBMT-GUI.exe location folder.
        layout.prop(context.scene.mmt_props, "path")

        # 获取DBMT.exe的路径
        dbmt_gui_exe_path = os.path.join(context.scene.mmt_props.path, "DBMT-GUI.exe")
        if not os.path.exists(dbmt_gui_exe_path):
            layout.label(text="错误:请选择DBMT-GUI.exe所在路径 ", icon='ERROR')
        
        row = layout.row()
        row.prop(context.scene, 'catter_game_name_enum')

        
        layout.prop(context.scene.mmt_props, "export_same_number", text="Keep Same Vertex Number.")

        # flip_tangent_w
        layout.prop(context.scene.mmt_props, "flip_tangent_w", text="Flip TANGENT.w")


        # row.operator("my.create_cube", text="Create Cube")


class CatterModelUI(bpy.types.Panel):
    bl_label = "Model"
    bl_idname = "CATTER_PT_MODEL_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        
        row = layout.row()
        row.prop(context.scene, "catter_drawib_input")

        row = layout.row()
        row.operator("catter.extract_model", text="Extract Model")

        row = layout.row()
        row.operator("catter.generate_mod", text="Generate Mod")


class IOPanel(bpy.types.Panel):
    bl_label = "IO" 
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

        current_game = bpy.context.scene.catter_game_name_enum
        # hoyogames use new architecture so can't use old import export method.
        if current_game not in ["HI3","GI","HSR","ZZZ","Unity-CPU-PreSkinning"]:
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

        # TODO 导出MMD的Bone Matrix，连续骨骼变换矩阵，并生成ini文件
        # TODO 重构完成Blender插件后开发此技术
        # layout.label(text="骨骼蒙皮动画Mod")
        # layout.prop(context.scene, "mmt_mmd_animation_mod_start_frame")
        # layout.prop(context.scene, "mmt_mmd_animation_mod_end_frame")
        # layout.prop(context.scene, "mmt_mmd_animation_mod_play_speed")
        # operator_export_mmd_bone_matrix = layout.operator("mmt.export_mmd_animation_mod", text="Export Animation Mod")
        # operator_export_mmd_bone_matrix.output_folder = output_folder_path

        # 添加分隔符
        # layout.separator()
        # layout.label(text="导入导出[新格式]")
        #  # 手动导入buf文件
        # operator_import_ib_vb = self.layout.operator("import_mesh.dbmt_buffer", text="导入Buffer模型文件")
        # operator_import_ib_vb.filepath = output_folder_path

        