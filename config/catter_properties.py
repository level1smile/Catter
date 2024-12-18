import bpy

from ..utils.vertexgroup_utils import *
from ..utils.dbmt_utils import * 

from bpy.props import FloatProperty



class OBJECT_OT_select_dbmt_folder(bpy.types.Operator):
    bl_idname = "object.select_dbmt_folder"
    bl_label = "Select DBMT Folder"

    directory: bpy.props.StringProperty(
        subtype='DIR_PATH',
        options={'HIDDEN'},
    ) # type: ignore

    def execute(self, context):
        scene = context.scene
        if self.directory:
            scene.dbmt.path = self.directory
            print(f"Selected folder: {self.directory}")
            # 在这里放置你想要执行的逻辑
            # 比如验证路径是否有效、初始化某些资源等
            DBMTUtils.save_dbmt_path()
            
            self.report({'INFO'}, f"Folder selected: {self.directory}")
        else:
            self.report({'WARNING'}, "No folder selected.")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# 全局配置用起来和管理起来都很方便，跟SpectrumQT学的。
class CatterProperties(bpy.types.PropertyGroup):
    # ------------------------------------------------------------------------------------------------------------
    path: bpy.props.StringProperty(
        name="DBMT-GUI.exe所在路径",
        description="插件需要先选择DBMT-GUI.exe的所在路径才能正常工作",
        default=DBMTUtils.load_dbmt_path(),
        subtype='DIR_PATH'
    ) # type: ignore

    # ------------------------------------------------------------------------------------------------------------
    model_extract_output_path: bpy.props.StringProperty(
        name="",
        description="FrameAnalysis提取出的模型文件默认存放路径",
        default="",
        subtype='DIR_PATH'
    ) # type: ignore

    # ------------------------------------------------------------------------------------------------------------
    # workspace_name: bpy.props.StringProperty(
    #     name="",
    #     description="当前DBMT-GUI中使用的工作空间",
    #     default=""
    # ) # type: ignore

    model_scale: FloatProperty(
        name="导入模型整体缩放比例",
        description="默认为1.0",
        default=1.0,
    ) # type: ignore
    # ------------------------------------------------------------------------------------------------------------
    workspace_namelist :bpy.props.EnumProperty (
        items= dbmt_get_workspace_namelist,
        name="工作空间",
        description="选择一个工作空间"
    ) # type: ignore

    # ------------------------------------------------------------------------------------------------------------
    generate_mod_after_export: bpy.props.BoolProperty(
        name="",
        description="在一键导出当前选中集合后，调用DBMT的生成二创模型方法，可以节省打开DBMT-GUI再点一下生成二创模型的时间",
        default=False
    ) # type: ignore

    export_same_number: bpy.props.BoolProperty(
        name="",
        description="导出时不改变顶点数 (在Unity-CPU-PreSkinning技术中常用，避免导出后顶点数变多导致无法和原本模型顶点数对应)",
        default=False
    ) # type: ignore

    export_normalize_all: bpy.props.BoolProperty(
        name="",
        description="导出时把模型自动规格化权重，防止忘记手动规格化导致模型塌陷问题。",
        default=False
    ) # type: ignore
    # ------------------------------------------------------------------------------------------------------------
    flip_tangent_w:bpy.props.BoolProperty(
        name="",
        description="翻转TANGENT.xyzw的w分量, 目前只有Unity游戏需要翻转这个w分量",
        default=False
    ) # type: ignore

    flip_tangent_z:bpy.props.BoolProperty(
        name="",
        description="翻转TANGENT.xyzw的z分量 (仅用于测试)",
        default=False
    ) # type: ignore

    flip_tangent_y:bpy.props.BoolProperty(
        name="",
        description="翻转TANGENT.xyzw的y分量 (仅用于测试)",
        default=False
    ) # type: ignore

    flip_tangent_x:bpy.props.BoolProperty(
        name="",
        description="翻转TANGENT.xyzw的x分量 (仅用于测试)",
        default=False
    ) # type: ignore
    # ------------------------------------------------------------------------------------------------------------
    flip_normal_w:bpy.props.BoolProperty(
        name="",
        description="翻转NORMAL.xyzw的w分量，只有有w分量的NORMAL才会被翻转w分量，因为大部分游戏的NORMAL都是NORMAL.xyz只有三个分量 (仅用于测试)",
        default=False
    ) # type: ignore

    flip_normal_z:bpy.props.BoolProperty(
        name="",
        description="翻转NORMAL.xyzw的z分量 (仅用于测试)",
        default=False
    ) # type: ignore

    flip_normal_y:bpy.props.BoolProperty(
        name="",
        description="翻转NORMAL.xyzw的y分量 (仅用于测试)",
        default=False
    ) # type: ignore

    flip_normal_x:bpy.props.BoolProperty(
        name="",
        description="翻转NORMAL.xyzw的x分量 (仅用于测试)",
        default=False
    ) # type: ignore

    import_merged_vgmap:bpy.props.BoolProperty(
        name="",
        description="导入时是否导入融合后的顶点组 (WWMI的合并顶点组技术会用到)",
        default=False
    ) # type: ignore

    # ------------------------------------------------------------------------------------------------------------
    credit_info_author_name: bpy.props.StringProperty(
        name="",
        description="Author's name.",
        default=""
    ) # type: ignore

    credit_info_author_social_link: bpy.props.StringProperty(
        name="",
        description="Author's social link.",
        default=""
    ) # type: ignore

    # ------------------------------------------------------------------------------------------------------------
    def __init__(self) -> None:
        super().__init__()
        # self.subtype = 'DIR_PATH'