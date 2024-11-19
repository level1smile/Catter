import os
import json
import bpy

def save_catter_launcher_path(path):
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    config = {'catter_launcher_path': bpy.context.scene.mmt_props.path}

    json_data = json.dumps(config)

    with open(config_path, 'w') as file:
        file.write(json_data)


def load_catter_launcher_path():
    script_path = os.path.abspath(__file__)

    plugin_directory = os.path.dirname(script_path)

    config_path = os.path.join(plugin_directory, 'Config.json')

    with open(config_path, 'r') as file:
        json_data = file.read()

    config = json.loads(json_data)

    return config['catter_launcher_path']



def game_items(self, context):
    items = []
    launcher_path = load_catter_launcher_path()
    games_path = os.path.join(launcher_path, "Games")
    gamename_list = os.listdir(games_path)
    for gamename in gamename_list:
        items.append(("OPTION_" + gamename,gamename,gamename))

    return items
