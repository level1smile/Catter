import bpy.props

from .ui.panel_ui import * 

from .ui.mesh_operator import *

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
    CatterProperties,
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
    Catter_MarkCollection_Toggle,

    # Config UI
    CatterConfigUI,

    # Migoto UI
    # CatterLauncherPathOperator,
    MigotoIOPanelDeprecated
    
)


# register properties
def catter_define_properties():
    bpy.types.Scene.mmt_mmd_animation_mod_start_frame = bpy.props.IntProperty(name="Start Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_end_frame = bpy.props.IntProperty(name="End Frame")
    bpy.types.Scene.mmt_mmd_animation_mod_play_speed = bpy.props.FloatProperty(name="Play Speed")


def register():
    catter_define_properties()
    for cls in register_classes:
        bpy.utils.register_class(cls)

     # 新建一个属性用来专门装MMT的路径
    bpy.types.Scene.dbmt = bpy.props.PointerProperty(type=CatterProperties)



    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func_migoto_right_click)
    bpy.types.OUTLINER_MT_collection.append(menu_dbmt_mark_collection_switch)


def unregister():
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func_migoto_right_click)
    bpy.types.OUTLINER_MT_collection.remove(menu_dbmt_mark_collection_switch)


if __name__ == "__main__":
    register()