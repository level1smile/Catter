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

    # 新建一个属性用来专门装MMT的路径
    bpy.types.Scene.mmt_props = bpy.props.PointerProperty(type=DBMTProperties)

    # MMT数值保存的变量
    bpy.types.Scene.mmt_mmd_animation_mod_start_frame = bpy.props.IntProperty(name="Start Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_end_frame = bpy.props.IntProperty(name="End Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_play_speed = bpy.props.FloatProperty(name="Play Speed")

    # 右键菜单
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func_migoto_right_click)

    bpy.types.OUTLINER_MT_collection.append(menu_dbmt_mark_collection_switch)

    # 在Blender退出前保存选择的MMT的路径
    bpy.app.handlers.depsgraph_update_post.append(save_mmt_path)

    
def unregister():
    # 取消注册所有类
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)

    # 退出时移除MMT路径变量
    del bpy.types.Scene.mmt_props

    # 退出时移除右键菜单
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func_migoto_right_click)


    bpy.types.OUTLINER_MT_collection.remove(menu_dbmt_mark_collection_switch)

    # 退出注册时删除MMT的MMD变量
    del bpy.types.Scene.mmt_mmd_animation_mod_start_frame
    del bpy.types.Scene.mmt_mmd_animation_mod_end_frame
    del bpy.types.Scene.mmt_mmd_animation_mod_play_speed


if __name__ == "__main__":
    register()