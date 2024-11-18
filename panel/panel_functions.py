import bpy
import os
import json


def save_mmt_path(path):
    # 获取当前脚本文件的路径
    script_path = os.path.abspath(__file__)

    # 获取当前插件的工作目录
    plugin_directory = os.path.dirname(script_path)

    # 构建保存文件的路径
    config_path = os.path.join(plugin_directory, 'Config.json')

    # 创建字典对象
    config = {'mmt_path': bpy.context.scene.mmt_props.path}

    # 将字典对象转换为 JSON 格式的字符串
    json_data = json.dumps(config)

    # 保存到文件
    with open(config_path, 'w') as file:
        file.write(json_data)


def load_mmt_path():
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
    return config['mmt_path']


# A enum for show games drop menu.
def game_items(self, context):
    items = [
        ('OPTION_GI', 'GI', 'Genshin Impact'),
        ('OPTION_HI3', 'HI3', 'Honkai Impact 3'),
        ('OPTION_HSR', 'HSR', 'Honkai StarRail'),
        ('OPTION_ZZZ', 'ZZZ', 'Zenless Zone Zero'),
        ('OPTION_WW', 'WW', 'Wuthering Waves'),
        ('OPTION_UnityCPUPreSkinning', 'Unity-CPU-PreSkinning', 'Unity Engine CPU-PreSkinning games')
    ]
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
