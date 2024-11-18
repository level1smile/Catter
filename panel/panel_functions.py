import bpy


# 定义属性的函数
def catter_define_properties():
    bpy.types.Scene.catter_drawib_input = bpy.props.StringProperty(
        name="DrawIB",
        description="Enter some drawib here",
        default=""
    )

# 删除属性的函数
def catter_remove_properties():
    del bpy.types.Scene.catter_drawib_input


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
