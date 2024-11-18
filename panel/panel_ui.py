import bpy

from .panel_functions import *


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

       



class CatterConfigUI(bpy.types.Panel):
    bl_label = "Config"
    bl_idname = "CATTER_PT_CONFIG_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Catter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, 'catter_game_name_enum')
        # row.operator("my.create_cube", text="Create Cube")



