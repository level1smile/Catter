import bpy.props

from .panel.panel_functions import *
from .panel.panel_ui import * 

from .menu.mesh_operator import *

from .migoto.migoto_import import *
from .migoto.migoto_export import *

from .buffer.buffer_import import *
from .buffer.buffer_export import *
from .buffer.animation_operator import *




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
    # Config UI
    CatterConfigUI,

    # Model UI
    CatterModelUI,
    # Buffer IO UI
    BufferIOPanel,

    # Extract Model
    ExtractModelOperator,
    GenerateModOperator,


    # migoto
    DBMTProperties,
    CatterLauncherPathOperator,
    MigotoIOPanelDeprecated,

    # 3Dmigoto ib和vb格式导入导出
    Import3DMigotoRaw,
    Export3DMigoto,

    # 新的Buffer格式导入导出
    Import_DBMT_Buffer,

    # MMT的一键快速导入导出
    MMTImportAllVbModel,
    MMTExportAllIBVBModel,

    # 多合一的一键快速导入导出
    DBMTImportAllVbModelMerged,
    DBMTExportMergedModVBModel,

    # mesh_operator 右键菜单栏
    RemoveUnusedVertexGroupOperator,
    MergeVertexGroupsWithSameNumber,
    FillVertexGroupGaps,
    AddBoneFromVertexGroup,
    RemoveNotNumberVertexGroup,
    ConvertToFragmentOperator,
    MMTDeleteLoose,
    MMTResetRotation,
    CatterRightClickMenu,
    SplitMeshByCommonVertexGroup,
    RecalculateTANGENTWithVectorNormalizedNormal,
    RecalculateCOLORWithVectorNormalizedNormal,
    # MMD类型动画Mod支持
    MMDModIniGenerator,

    # Collection's right click menu item.
    Catter_MarkCollection_Switch,
    Catter_MarkCollection_Toggle
    
)


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

    bpy.types.Scene.catter_game_type_enum = bpy.props.EnumProperty(
        name="DataType",
        description="Choose a data type",
        items=get_game_types
    )

    

    bpy.types.Scene.mmt_props = bpy.props.PointerProperty(type=DBMTProperties)

    bpy.types.Scene.mmt_mmd_animation_mod_start_frame = bpy.props.IntProperty(name="Start Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_end_frame = bpy.props.IntProperty(name="End Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_play_speed = bpy.props.FloatProperty(name="Play Speed")




# delete properties
def catter_remove_properties():
    del bpy.types.Scene.mmt_props

    del bpy.types.Scene.catter_drawib_input
    del bpy.types.Scene.catter_game_name_enum

    del bpy.types.Scene.mmt_mmd_animation_mod_start_frame
    del bpy.types.Scene.mmt_mmd_animation_mod_end_frame
    del bpy.types.Scene.mmt_mmd_animation_mod_play_speed


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)

    catter_define_properties()


    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func_migoto_right_click)
    bpy.types.OUTLINER_MT_collection.append(menu_dbmt_mark_collection_switch)

    bpy.app.handlers.depsgraph_update_post.append(save_catter_launcher_path)

def unregister():
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)

    catter_remove_properties()

    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func_migoto_right_click)
    bpy.types.OUTLINER_MT_collection.remove(menu_dbmt_mark_collection_switch)


if __name__ == "__main__":
    register()