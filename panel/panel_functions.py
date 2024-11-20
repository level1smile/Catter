import bpy
import os
import json

from ..core.games.extract_model import *
from ..migoto.migoto_utils import *
from .panel_utils import *


class ExtractModelOperator(bpy.types.Operator):
    bl_idname = "catter.extract_model"
    bl_label = "Extract Model"

    def execute(self, context):
        # combine global config.
        current_game = bpy.context.scene.catter_game_name_enum
        loader_path = os.path.join(bpy.context.scene.mmt_props.path,"Games\\" )
        config_path = os.path.join(bpy.context.scene.mmt_props.path,"Configs\\ExtractTypes\\" + current_game + "\\")
        g = GlobalConfig(GameName=current_game,GameLoaderPath=loader_path,ConfigFolderPath=config_path)

        # get draw ib list.
        draw_ib_list = get_draw_ib_list(context.scene.catter_drawib_input)
        if len(draw_ib_list) == 0:
            # TODO add auto detect all draw_ib with pointlist index.
            self.report({'ERROR'},"Please at least fill one DrawIB to extract.")
        else:
            # call extract.
            unity_extract_model(global_config=g,draw_ib_list=draw_ib_list)

        self.report({'INFO'}, "Extract Model.")
        return {'FINISHED'}
    

class GenerateModOperator(bpy.types.Operator):
    bl_idname = "catter.generate_mod"
    bl_label = "Generate Mod"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        self.report({'INFO'}, "Generate Mod Success.")
        return {'FINISHED'}
    

class DBMTProperties(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(
        name="Launcher",
        description="Choose catter launcher path",
        default=load_catter_launcher_path(),
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


class CatterLauncherPathOperator(bpy.types.Operator):
    bl_idname = "catter.select_launcher_folder"
    bl_label = "Select Folder"

    def execute(self, context):
        bpy.ops.ui.directory_dialog('INVOKE_DEFAULT', directory=context.scene.mmt_props.path)
        return {'FINISHED'}