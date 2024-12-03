import bpy

def get_current_workspace_name()->str:
    return bpy.context.scene.dbmt.workspace_namelist