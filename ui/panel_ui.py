import bpy
import os
import json

from ..migoto.migoto_utils import *



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



class CatterProperties(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name="主路径",
        description="选择DBMT的主路径",
        default=load_dbmt_path(),
        subtype='DIR_PATH'
    ) # type: ignore

    export_same_number: bpy.props.BoolProperty(
        name="Export Object With Same Number As It's Import",
        description="Export doesn't change number",
        default=False
    ) # type: ignore

    flip_tangent_w:bpy.props.BoolProperty(
        name="",
        description="翻转TANGENT的W分量",
        default=False
    ) # type: ignore

    def __init__(self) -> None:
        super().__init__()
        # self.subtype = 'DIR_PATH'


# class CatterLauncherPathOperator(bpy.types.Operator):
#     bl_idname = "catter.select_launcher_folder"
#     bl_label = "Select Folder"

#     def execute(self, context):
#         bpy.ops.ui.directory_dialog('INVOKE_DEFAULT', directory=context.scene.dbmt.path)
#         return {'FINISHED'}


class CatterConfigUI(bpy.types.Panel):
    bl_label = "Config"
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
        row.label(text="Current Game: " + get_current_game_from_main_json())

        layout.prop(context.scene.dbmt, "export_same_number", text="Keep Same Vertex Number.")
        layout.prop(context.scene.dbmt, "flip_tangent_w", text="Flip TANGENT.w")


class MigotoIOPanelDeprecated(bpy.types.Panel):
    bl_label = "3Dmigoto" 
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



        