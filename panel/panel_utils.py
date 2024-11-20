import os
import json
import bpy

from ..core.utils.dbmt_file_utils import *

# save launcher path to cached config.
def save_catter_launcher_path(path):
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    config = {'catter_launcher_path': bpy.context.scene.mmt_props.path}

    json_data = json.dumps(config)

    with open(config_path, 'w') as file:
        file.write(json_data)

# read cached config for launcher path.
def load_catter_launcher_path():
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    with open(config_path, 'r') as file:
        json_data = file.read()

    config = json.loads(json_data)

    return config['catter_launcher_path']


# read game names from launcher's config.
def game_items(self, context):
    items = []
    launcher_path = load_catter_launcher_path()
    games_path = os.path.join(launcher_path, "Games")
    gamename_list = os.listdir(games_path)
    for gamename in gamename_list:
        items.append((gamename,gamename,gamename))

    return items


# read game type name from launcher's config path.
def get_game_types(self,context):
    game_types = []
    game_types.append(("Auto","Auto","Auto"))
    launcher_path = load_catter_launcher_path()
    currentgame = bpy.context.scene.catter_game_name_enum
    extract_type_path = os.path.join(launcher_path, "Configs\\ExtractTypes\\" + currentgame)
    gametype_list = dbmt_fileutil__list_files(extract_type_path)

    for gametype_filename in gametype_list:
        if ".json" in gametype_filename:
            gametype_name = gametype_filename[0:len(gametype_filename) - 5]
            # print(gametype_name)
            game_types.append((gametype_name,gametype_name,gametype_name))

    return game_types


# get draw ib list from draw ib textbox input.
def get_draw_ib_list(draw_ib_value:str) ->list:
    # get draw ib list.
    draw_ib_list = []
    if "," in draw_ib_value:
        drawib_splits = draw_ib_value.split(",")
        for draw_ib in drawib_splits:
            draw_ib_trim = draw_ib.strip()
            draw_ib_list.append(draw_ib_trim)
    elif draw_ib_value.strip() != "":
            draw_ib_list.append(draw_ib_value.strip())
    return draw_ib_list

