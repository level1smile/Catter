import os
import bpy
import json
import subprocess
from .property_utils import *

# TODO 不应该写单独的方法，否则会导致缺少类似命名空间的限制功能，导致调用的时候难以区分不同方法。
class DBMTUtils:

    @classmethod
    def save_dbmt_path(cls):
        # 获取当前脚本文件的路径
        script_path = os.path.abspath(__file__)

        # 获取当前插件的工作目录
        plugin_directory = os.path.dirname(script_path)

        # 构建保存文件的路径
        config_path = os.path.join(plugin_directory, 'Config.json')

        # 创建字典对象
        config = {'dbmt_path': bpy.context.scene.dbmt.path}

        # 将字典对象转换为 JSON 格式的字符串
        json_data = json.dumps(config)

        # 保存到文件
        with open(config_path, 'w') as file:
            file.write(json_data)

    @classmethod
    def load_dbmt_path(cls):
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
        return config['dbmt_path']

    @classmethod
    # Read Main.json from DBMT folder and then get current game name.
    def get_current_game_from_main_json(cls,in_path="") ->str:
        current_game = ""
        if in_path == "":
            in_path = bpy.context.scene.dbmt.path

        main_setting_path = os.path.join(in_path, "Configs\\Main.json")
        # print(main_setting_path)
        if os.path.exists(main_setting_path):
            main_setting_file = open(main_setting_path)
            main_setting_json = json.load(main_setting_file)
            main_setting_file.close()
            current_game = main_setting_json["GameName"]
        # print(current_game)
        return current_game

    # Read Main.json from DBMT folder and then get current workspace name.
    @classmethod
    def get_current_workspacename_from_main_json(cls,in_path="") ->str:
        current_workspacename = ""
        if in_path == "":
            in_path = bpy.context.scene.dbmt.path

        main_setting_path = os.path.join(in_path, "Configs\\Main.json")
        # print(main_setting_path)
        if os.path.exists(main_setting_path):
            main_setting_file = open(main_setting_path)
            main_setting_json = json.load(main_setting_file)
            main_setting_file.close()
            current_workspacename = main_setting_json.get("WorkSpaceName","")
        # print(current_game)
        return current_workspacename


    # Get current output folder.
    @classmethod
    def get_output_folder_path(cls) -> str:
        mmt_path = bpy.context.scene.dbmt.path

        current_game = DBMTUtils.get_current_game_from_main_json()
        output_folder_path = mmt_path + "Games\\" + current_game + "\\3Dmigoto\\Mods\\output\\"
        return output_folder_path


    # Get Games\\xxx\\Config.json path.
    # Deprecated 
    @classmethod
    def get_game_config_json_path_Deprecated(cls)->str:
        current_game =  DBMTUtils.get_current_game_from_main_json()
        return os.path.join(bpy.context.scene.dbmt.path, "Games\\" + current_game + "\\Config.json")


    # Get drawib list from Game's Config.json.
    @classmethod
    def get_extract_drawib_list_from_workspace_config_json(cls)->list:
        workspace_path = DBMTUtils.dbmt_get_workspace_path(DBMTUtils.get_current_workspacename_from_main_json())

        game_config_path = os.path.join(workspace_path,"Config.json")
        game_config_file = open(game_config_path)
        game_config_json = json.load(game_config_file)
        game_config_file.close()

        # draw_ib_list =game_config_json["DrawIBList"]
        draw_ib_list = []
        for item in game_config_json:
            drawib_value = item["DrawIB"]
            draw_ib_list.append(drawib_value)

        return draw_ib_list


    # Get every drawib folder path from output folder.
    @classmethod
    def get_import_drawib_folder_path_dict_Deprecated(cls)->list:
        output_folder_path = DBMTUtils.dbmt_get_workspace_path()
        draw_ib_list = DBMTUtils.get_extract_drawib_list_from_workspace_config_json()
        import_folder_path_dict = {}
        for draw_ib in draw_ib_list:
            # print("DrawIB:", draw_ib)
            import_folder_path_dict[draw_ib] = os.path.join(output_folder_path, draw_ib)
        return import_folder_path_dict

    @classmethod
    def get_import_drawib_folder_path_dict_with_first_match_type(cls,workspace_folder_path:str)->list:
        output_folder_path = workspace_folder_path
        draw_ib_list = DBMTUtils.get_extract_drawib_list_from_workspace_config_json()
        
        final_import_folder_path_dict = {}

        for draw_ib in draw_ib_list:
            gpu_import_folder_path_list = []
            cpu_import_folder_path_list = []

            # print("DrawIB:", draw_ib)
            import_drawib_folder_path = os.path.join(output_folder_path, draw_ib)

            if not os.path.exists(import_drawib_folder_path):
                continue

            dirs = os.listdir(import_drawib_folder_path)
            for dirname in dirs:
                if not dirname.startswith("TYPE_"):
                    continue
                final_import_folder_path = os.path.join(import_drawib_folder_path,dirname)
                if dirname.startswith("TYPE_GPU"):
                    gpu_import_folder_path_list.append(final_import_folder_path)
                elif dirname.startswith("TYPE_CPU"):
                    cpu_import_folder_path_list.append(final_import_folder_path)

            if len(gpu_import_folder_path_list) != 0:
                final_import_folder_path_dict[draw_ib] = gpu_import_folder_path_list[0]
            elif len(cpu_import_folder_path_list) != 0:
                final_import_folder_path_dict[draw_ib] = cpu_import_folder_path_list[0]
            else:
                pass
                # raise ImportError()

        return final_import_folder_path_dict


    # Read import model name list from tmp.json.
    # TODO Deprecated 
    @classmethod
    def get_prefix_list_from_tmp_json(cls,import_folder_path:str) ->list:
        
        tmp_json_path = os.path.join(import_folder_path, "tmp.json")

        drawib = os.path.basename(import_folder_path)

        if os.path.exists(tmp_json_path):
            tmp_json_file = open(tmp_json_path)
            tmp_json = json.load(tmp_json_file)
            tmp_json_file.close()
            import_prefix_list = tmp_json["ImportModelList"]
            if len(import_prefix_list) == 0:
                import_partname_prefix_list = []
                partname_list = tmp_json["PartNameList"]
                for partname in partname_list:
                    import_partname_prefix_list.append(drawib + "-" + partname)
                return import_partname_prefix_list
            else:
                # import_prefix_list.sort() it's naturally sorted in DBMT so we don't need sort here.
                return import_prefix_list
        else:
            return []


    # Read model prefix attribute in fmt file to locate .ib and .vb file.
    # Save lots of space when reverse mod which have same stride but different kinds of D3D11GameType.
    @classmethod
    def get_model_prefix_from_fmt_file(cls,fmt_file_path:str)->str:
        with open(fmt_file_path, 'r') as file:
            for i in range(10):  
                line = file.readline().strip()
                if not line:
                    continue
                if line.startswith('prefix:'):
                    return line.split(':')[1].strip()  
        return ""  

    @classmethod
    def dbmt_run_command(cls,command_str:str):
        dbmt_path = bpy.context.scene.dbmt.path

        run_input_json_path = os.path.join(dbmt_path,"Configs\\RunInput.json")
        run_input_dict = {"RunCommand":command_str,"WorkSpaceName":bpy.context.scene.dbmt.workspace_namelist}
        run_input_json = json.dumps(run_input_dict)
        with open(run_input_json_path, 'w') as run_input_json_file:
            run_input_json_file.write(run_input_json)

        run_result_json_path = os.path.join(dbmt_path,"Configs\\RunResult.json")
        run_result_dict = {"result":"Unknown Error!"}
        run_result_json = json.dumps(run_result_dict)
        with open(run_result_json_path, 'w') as run_result_json_file:
            run_result_json_file.write(run_result_json)

        dbmt_plugin_path = os.path.join(dbmt_path,"Plugins\\")
        dbmt_core_path = os.path.join(dbmt_plugin_path,"DBMT.exe")
        # 运行一个外部的 .exe 文件
        result = subprocess.run([dbmt_core_path],cwd=dbmt_plugin_path)

        
    @classmethod
    def dbmt_get_run_result(cls) -> str:
        dbmt_path = bpy.context.scene.dbmt.path
        run_result_json_path = os.path.join(dbmt_path,"Configs\\RunResult.json")
        with open(run_result_json_path, 'r', encoding='utf-8') as file:
            run_result_json = json.load(file)
        if "result" in run_result_json:
            result = run_result_json["result"]
            return result
        else:
            return "Unknown error lead to bad json format!"

    @classmethod
    def dbmt_run_generate_mod(cls,workspace_name:str) -> str:
        DBMTUtils.dbmt_run_command("split")
        run_result = DBMTUtils.dbmt_get_run_result()
        if run_result == "success":
            subprocess.run(['explorer',os.path.join(DBMTUtils.dbmt_get_workspace_path(workspace_name),"GeneratedMod\\")])
        return run_result
    @classmethod
    def dbmt_get_workspace_path(cls,workspace_name:str) -> str:
        if workspace_name != "":
            workspaced_outputfolder = DBMTUtils.get_output_folder_path() + workspace_name + "\\"
            return workspaced_outputfolder
        else:
            return DBMTUtils.get_output_folder_path()
    
# ------------------------------------------------------------------------------------------------------
# 带有elf,context的都是特殊方法，不能放到工具类中,只能漏在外面
def dbmt_get_workspace_namelist(self,context):
    directory_path = DBMTUtils.get_output_folder_path()
    if not os.path.isdir(directory_path):
        return []
    
    # 获取所有子目录
    directories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    workspace_namelist = []
    for dirname in directories:
        workspace_namelist.append((dirname,dirname,dirname))

    return workspace_namelist


    
