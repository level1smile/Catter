import bpy

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


# register properties
def catter_define_properties():
    bpy.types.Scene.catter_drawib_input = bpy.props.StringProperty(
        name="DrawIB",
        description="Enter some drawib here",
        default=""
    )

    bpy.types.Scene.catter_game_name_enum = bpy.props.EnumProperty(
        name="Game",
        description="Choose a work game",
        items=game_items
    )


# delete properties
def catter_remove_properties():
    del bpy.types.Scene.catter_drawib_input
    del bpy.types.Scene.catter_game_name_enum



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
