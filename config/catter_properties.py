import bpy

from ..utils.vertexgroup_utils import *
from ..utils.dbmt_utils import * 

# 全局配置用起来和管理起来都很方便，跟SpectrumQT学的。
class CatterProperties(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name="DBMT-GUI.exe所在路径",
        description="插件需要先选择DBMT-GUI.exe的所在路径才能正常工作",
        default=load_dbmt_path(),
        subtype='DIR_PATH'
    ) # type: ignore

    model_extract_output_path: bpy.props.StringProperty(
        name="",
        description="FrameAnalysis提取出的模型文件默认存放路径",
        default="",
        subtype='DIR_PATH'
    ) # type: ignore


    draw_ib_input_text: bpy.props.StringProperty(
        name="",
        description="DrawIB指绘制时使用的IndexBuffer的Hash指，输入多个DrawIB用逗号隔开",
        default=""
    ) # type: ignore

    model_workspace_name: bpy.props.StringProperty(
        name="",
        description="工作空间名称,手动输入名称则会提取到上面设置的默认路径下并以此名称创建新文件夹存储，手动点击按钮选择路径则会存储到选择的路径中",
        default="",
        subtype='DIR_PATH'
    ) # type: ignore


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

    def __init__(self) -> None:
        super().__init__()
        # self.subtype = 'DIR_PATH'