# 频繁使用的属性放到这里，因为bpy.context.scene.dbmt这个前缀太长了而且不好记忆
import bpy


def get_current_workspace_name()->str:
    return bpy.context.scene.dbmt.workspace_namelist

def get_mmt_path()->str:
    return bpy.context.scene.dbmt.path
