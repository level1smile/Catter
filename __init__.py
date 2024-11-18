import bpy.props

bl_info = {
    "name": "Catter",
    "description": "A blender plugin for game mod with 3Dmigoto.",
    "maintainer":"NicoMico",
    "blender": (4, 2, 3),
    "version": (1, 0, 0),
    "location": "View3D",
    "category": "Generic"
}

register_classes = (
    
)


def register():
    # 注册所有类
    for cls in register_classes:
        bpy.utils.register_class(cls)

def unregister():
    # 取消注册所有类
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()