import bpy
import os
import json


def save_catter_launcher_path(path):
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    config = {'catter_launcher_path': bpy.context.scene.mmt_props.path}

    json_data = json.dumps(config)

    with open(config_path, 'w') as file:
        file.write(json_data)


def load_catter_launcher_path():
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    with open(config_path, 'r') as file:
        json_data = file.read()

    config = json.loads(json_data)

    return config['catter_launcher_path']


def game_items(self, context):
    items = []
    launcher_path = load_catter_launcher_path()
    games_path = os.path.join(launcher_path, "Games")
    gamename_list = os.listdir(games_path)
    for gamename in gamename_list:
        items.append(("OPTION_" + gamename,gamename,gamename))

    return items


class DrawIBInputOperator(bpy.types.Operator):
    bl_idname = "catter.drawib_input"
    bl_label = "DrawIB Input"

    def execute(self, context):
        input_value = context.scene.catter_drawib_input
        self.report({'INFO'}, f"Input 1: {input_value}")
        return {'FINISHED'}
    

class ExtractModelOperator(bpy.types.Operator):
    bl_idname = "catter.extract_model"
    bl_label = "Extract Model"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        self.report({'INFO'}, "Cube created")
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
        self.subtype = 'DIR_PATH'
        self.path = load_catter_launcher_path()


class CatterLauncherPathOperator(bpy.types.Operator):
    bl_idname = "catter.select_launcher_folder"
    bl_label = "Select Folder"

    def execute(self, context):
        bpy.ops.ui.directory_dialog('INVOKE_DEFAULT', directory=context.scene.mmt_props.path)
        return {'FINISHED'}