import os
import shutil
from core.common.buffer_file import IndexBufferBufFile, FmtFile
from core.common.global_config import GlobalConfig
from core.utils.dbmt_log_utils import log_newline

# 由 吃饼喝茶 改进的 v0.1版本

# 手动反转3D模型文件，仅支持Unity顶点着色器的预皮肤处理mod反转。
# 当前稳定支持的游戏列表：原神、崩坏：星穹铁道、崩坏3、绝区零。
def main():
    # 1. 你的mod文件位置在哪里？填写到mod_root_folder中。
    mod_root_folder = "G:\\games\\zzz_tool\\XXMI-LAUNCHER-PACKAGE-v1.0.4\\ZZMI\\Mods\\Exce - Ellen Joe\\2-Ellen-FullNude\\"

    # 2. 将索引缓冲区文件路径添加到index_buffer_filepath_list中。
    index_buffer_filepath_list = [
        os.path.join(mod_root_folder, "EllenHairA.ib"),
        os.path.join(mod_root_folder, "EllenBodyA.ib")
    ]

    # 3. 填写一个包含类别名和缓冲文件路径的字典，包含所有缓冲文件路径。
    category_name_buf_file_path_dict_all = {
        "EllenHairA.ib": {
            "Position": os.path.join(mod_root_folder, "EllenHairPosition.buf"),
            "Texcoord": os.path.join(mod_root_folder, "EllenHairTexcoord.buf"),
            "Blend": os.path.join(mod_root_folder, "EllenHairBlend.buf")
        },
        "EllenBodyA.ib": {
            "Position": os.path.join(mod_root_folder, "EllenBodyPosition.buf"),
            "Texcoord": os.path.join(mod_root_folder, "EllenBodyTexcoord.buf"),
            "Blend": os.path.join(mod_root_folder, "EllenBodyBlend.buf")
        }
    }

    # 触发自动游戏类型检测，以了解它使用的所有可能的GameType。
    g = GlobalConfig(
        GameName="ZZZ",
        ConfigFolderPath="D:\\3d_asset_project\\input_or_output_tools\\DBMT-1.0.9.1\\configs\\",
        GameLoaderPath="G:\\games\\zzz_tool\\DBMT-Release-V1.0.9.1\\Games\\ZZZ\\3Dmigoto"
    )

    # 对每个索引缓冲区文件分别进行检测和处理
    for ib_file_path in index_buffer_filepath_list:
        ib_filename = os.path.basename(ib_file_path)
        category_name_buf_file_path_dict = category_name_buf_file_path_dict_all[ib_filename]

        matched_gametypename_list = g.D3D11GameTypeConfig.detect_game_type(category_name_buf_file_path_dict=category_name_buf_file_path_dict, reverse=True)
        print(matched_gametypename_list)

        # 创建mod输出文件夹。
        output_folder_path = os.path.join(mod_root_folder, "Reverse")
        os.makedirs(output_folder_path, exist_ok=True)

        # 为每个游戏类型组合fmt文件并输出最终的.vb文件，并将.ib文件移到那里。
        for gametypename in matched_gametypename_list:
            d3d11gametype = g.D3D11GameTypeConfig.GameTypeName_D3D11GameType_Dict[gametypename]
            vb_bytearray = d3d11gametype.combine_buf_files_to_vb_file_bytearray(category_name_buf_file_path_dict)

            filename_prefix = f"{d3d11gametype.GameTypeName}-{os.path.splitext(ib_filename)[0]}"

            # 将我们指定的每个.ib文件复制到mod反转文件夹。
            shutil.copy2(ib_file_path, os.path.join(output_folder_path, f"{filename_prefix}.ib"))

            # 写入我们的.vb文件，我们只需要1个.vb文件来包含所有.ib和.fmt文件。
            output_vb_filepath = os.path.join(output_folder_path, f"{filename_prefix}.vb")
            with open(output_vb_filepath, 'wb') as vb_file:
                vb_file.write(vb_bytearray)

            # 写入fmt文件。
            output_fmt_filepath = os.path.join(output_folder_path, f"{filename_prefix}.fmt")
            fmt_file = FmtFile()
            fmt_file.D3d11GameTypeObj = d3d11gametype
            fmt_file.write_to_file(write_file_path=output_fmt_filepath, ib_stride=4, prefix=filename_prefix)

if __name__ == "__main__":
    main()
