import re
import numpy
import operator  # to get function names for operators like @, +, -
import struct
import os
import bpy
import json

main_json_path = ""

from glob import glob

def matmul(a, b):
    return operator.matmul(a, b)  # the same as writing a @ b


def keys_to_ints(d):
    return {k.isdecimal() and int(k) or k: v for k, v in d.items()}


def keys_to_strings(d):
    return {str(k): v for k, v in d.items()}


# This used to catch any exception in run time and raise it to blender output console.
class Fatal(Exception):
    pass


f32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_FLOAT''')
f16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_FLOAT''')
u32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_UINT''')
u16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_UINT''')
u8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_UINT''')
s32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_SINT''')
s16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_SINT''')
s8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_SINT''')
unorm16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_UNORM''')
unorm8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_UNORM''')
snorm16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_SNORM''')
snorm8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_SNORM''')

misc_float_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD][0-9]+)+_(?:FLOAT|UNORM|SNORM)''')
misc_int_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD][0-9]+)+_[SU]INT''')


def EncoderDecoder(fmt):
    if f32_pattern.match(fmt):
        return (lambda data: b''.join(struct.pack('<f', x) for x in data),
                lambda data: numpy.frombuffer(data, numpy.float32).tolist())
    if f16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.float16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.float16).tolist())
    if u32_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint32).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint32).tolist())
    if u16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint16).tolist())
    if u8_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint8).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint8).tolist())
    if s32_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int32).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int32).tolist())
    if s16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int16).tolist())
    if s8_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int8).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int8).tolist())

    if unorm16_pattern.match(fmt):
        return (
            lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 65535.0)).astype(numpy.uint16).tobytes(),
            lambda data: (numpy.frombuffer(data, numpy.uint16) / 65535.0).tolist())
    if unorm8_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 255.0)).astype(numpy.uint8).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.uint8) / 255.0).tolist())
    if snorm16_pattern.match(fmt):
        return (
            lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 32767.0)).astype(numpy.int16).tobytes(),
            lambda data: (numpy.frombuffer(data, numpy.int16) / 32767.0).tolist())
    if snorm8_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 127.0)).astype(numpy.int8).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.int8) / 127.0).tolist())
    print(fmt)
    raise Fatal('File uses an unsupported DXGI Format: %s' % fmt)


components_pattern = re.compile(r'''(?<![0-9])[0-9]+(?![0-9])''')

def format_components(fmt):
    return len(components_pattern.findall(fmt))


def format_size(fmt):
    matches = components_pattern.findall(fmt)
    return sum(map(int, matches)) // 8


# Read Main.json from DBMT folder and then get current game name.
# def get_current_game_from_main_json(in_path="") ->str:
#     current_game = ""
#     if in_path == "":
#         in_path = bpy.context.scene.mmt_props.path

#     main_setting_path = os.path.join(in_path, "Configs\\Main.json")
#     # print(main_setting_path)
#     if os.path.exists(main_setting_path):
#         main_setting_file = open(main_setting_path)
#         main_setting_json = json.load(main_setting_file)
#         main_setting_file.close()
#         current_game = main_setting_json["GameName"]
#     # print(current_game)
#     return current_game


# Get current output folder.
def get_output_folder_path() -> str:
    mmt_path = bpy.context.scene.mmt_props.path
    current_game = bpy.context.scene.catter_game_name_enum
    output_folder_path = mmt_path + "Games\\" + current_game + "\\3Dmigoto\\Mods\\output\\"
    return output_folder_path


# Get mmt path from bpy.context.scene.mmt_props.path.
def get_mmt_path()->str:
    return bpy.context.scene.mmt_props.path


# Get Games\\xxx\\Config.json path.
def get_game_config_json_path()->str:
    return os.path.join(bpy.context.scene.mmt_props.path, "Games\\" + bpy.context.scene.catter_game_name_enum + "\\Config.json")


# Get drawib list from Game's Config.json.
def get_extract_drawib_list_from_game_config_json()->list:
    game_config_path = get_game_config_json_path()
    game_config_file = open(game_config_path)
    game_config_json = json.load(game_config_file)
    game_config_file.close()
    draw_ib_list = []
    for ib_config in game_config_json:
        draw_ib = ib_config["DrawIB"]
        draw_ib_list.append(draw_ib)

    return draw_ib_list


# Get every drawib folder path from output folder.
def get_import_drawib_folder_path_list()->list:
    output_folder_path = get_output_folder_path()
    draw_ib_list = get_extract_drawib_list_from_game_config_json()
    import_folder_path_list = []
    for draw_ib in draw_ib_list:
        # print("DrawIB:", draw_ib)
        import_folder_path_list.append(os.path.join(output_folder_path, draw_ib))
    return import_folder_path_list


# Read import model name list from tmp.json.
def get_prefix_list_from_tmp_json(import_folder_path:str) ->list:
    
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


# Recursive select every object in a collection and it's sub collections.
def select_collection_objects(collection):
    def recurse_collection(col):
        for obj in col.objects:
            obj.select_set(True)
        for subcol in col.children_recursive:
            recurse_collection(subcol)

    recurse_collection(collection)


# Read model prefix attribute in fmt file to locate .ib and .vb file.
# Save lots of space when reverse mod which have same stride but different kinds of D3D11GameType.
def get_model_prefix_from_fmt_file(fmt_file_path:str)->str:
    with open(fmt_file_path, 'r') as file:
        for i in range(10):  
            line = file.readline().strip()
            if not line:
                continue
            if line.startswith('prefix:'):
                return line.split(':')[1].strip()  
    return ""  


