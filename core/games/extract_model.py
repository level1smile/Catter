from ..common.global_config import *

import shutil

def unity_auto_gametype(draw_ib:str,global_config:GlobalConfig):
    fadata = FrameAnalysisData(global_config.WorkFolder)
    falog = FrameAnalysisLog(global_config.WorkFolder)

    # auto detect game type
    possible_gametype_list:list[D3D11GameType] = []

    for gametype in global_config.D3D11GameTypeConfig.Ordered_GPU_CPU_D3D11GameTypeList:
        log_info("Current detect gametype: " + gametype.GameTypeName)

        # if TEXCOORD in TrianglelistIndex, we use TEXCOORD , or we use POSITION
        detect_element_name = ""
        if gametype.ElementNameD3D11ElementDict["TEXCOORD"].ExtractTechnique == "trianglelist":
            detect_element_name = "TEXCOORD"
        else:
            detect_element_name = "POSITION"
        
        detect_category = gametype.ElementNameD3D11ElementDict[detect_element_name].Category
        detect_slot = gametype.CategoryExtractSlotDict[detect_category]
        detect_stride = gametype.CategoryStrideDict[detect_category]

        trianglelist_index_list= falog.get_index_list_by_draw_ib(draw_ib=draw_ib,only_match_first=False)

        trianglelist_extract_index = ""
        vertex_count = 0
        for trianglelist_index in trianglelist_index_list:
            # log_info("Index: " + trianglelist_index)
            detect_filename_list =fadata.filter_filename(trianglelist_index + "-" + detect_slot,".buf")
            if len(detect_filename_list) == 0:
                continue
            detect_filepath = os.path.join(fadata.WorkFolder,detect_filename_list[0])
            detect_file_size = os.path.getsize(detect_filepath)
            vertex_count = detect_file_size / detect_stride
            trianglelist_extract_index = trianglelist_index
            break
        
        pointlist_extract_index = falog.get_pointlist_index_by_draw_ib(draw_ib=draw_ib)

        # log_info("Trianglelist Extract Index: " + trianglelist_extract_index)
        # log_info("Pointlist Extract Index: " + pointlist_extract_index)

        log_info("Detect ElementName: " + detect_element_name + " detect_slot: " + str(detect_slot) + " detect_stride:" + str(detect_stride))

        log_info("Detect FileSize: " +str(detect_file_size) +" Assume VertexCount: " + str(vertex_count))

        # read every slot file to validate gametype.
        all_category_match = True
        for category_name,category_slot in gametype.CategoryExtractSlotDict.items():
            category_stride = gametype.CategoryStrideDict[category_name]
            category_extract_technique = gametype.CategoryExtractTechniqueDict[category_name]

            category_extract_index = trianglelist_extract_index
            if category_extract_technique == "pointlist":
                category_extract_index = pointlist_extract_index
            
            log_info("category_name: " + category_name + " extract technique: " + category_extract_technique + " category stride: " + str(category_stride))
            
            category_filename_list =  fadata.filter_filename(category_extract_index + "-" + category_slot, ".buf")
            if len(category_filename_list) == 0:
                log_warning_str("can't find category_filename_list for: " + category_slot)
                all_category_match = False
                break

            category_filename = category_filename_list[0]
            category_filepath = os.path.join(fadata.WorkFolder, category_filename)
            category_filesize = os.path.getsize(category_filepath)
            category_vertex_count = category_filesize / category_stride
            log_info("assume vertexcount: " + str(vertex_count) + " category_vertex_count: " + str(category_filesize) + " / " + str(category_stride) + " = " + str(category_vertex_count))

            if category_vertex_count != vertex_count:
                all_category_match = False
                log_warning_str("categpry vertex count not match " + category_slot)
                break
        
        if all_category_match:
            log_warning_str("GameType Matched: " + gametype.GameTypeName)
            possible_gametype_list.append(gametype)
        else:
            log_warning_str("not all category match")
        log_newline()
    
    log_info("all matched gametype:")
    for gametype in possible_gametype_list:
        log_info(gametype.GameTypeName)
    log_newline()

    matched_game_type = ""

    if len(possible_gametype_list) == 1:
        matched_game_type = possible_gametype_list[0].GameTypeName
    else:

        gpu_preskinning_number = 0
        cpu_preskinning_number = 0
        for gametype in possible_gametype_list:
            if gametype.GPU_PreSkinning:
                gpu_preskinning_number = gpu_preskinning_number + 1
            else:
                cpu_preskinning_number = cpu_preskinning_number + 1
        
        if gpu_preskinning_number == 1:
            matched_game_type = possible_gametype_list[0].GameTypeName
        elif gpu_preskinning_number > 1:
            log_warning_str("more than 1 GPU-PreSkinning gametype matched.")
        elif cpu_preskinning_number > 1:
            log_warning_str("more than 1 CPU-PreSkinning gametype matched.")
        else:
            log_warning_str("no any gametype matched.")

    return matched_game_type,trianglelist_extract_index,pointlist_extract_index
    
        
    
def unity_extract_model(draw_ib_list,global_config:GlobalConfig):
    fadata = FrameAnalysisData(global_config.WorkFolder)
    falog = FrameAnalysisLog(global_config.WorkFolder)

    log_info("Start to extract model:")
    for draw_ib in draw_ib_list:
        log_info("Current DrawIB: " + draw_ib)

        matched_game_type, trianglelist_extract_index, pointlist_extract_index = unity_auto_gametype(draw_ib=draw_ib,global_config=global_config)
        log_info("Matched GameType: " + matched_game_type)

        draw_ib_config = DrawIBConfig(DrawIB=draw_ib,GameTypeName=matched_game_type)

        # Create model extract output folder.
        draw_ib_config.DrawIBOutputFolder = os.path.join(global_config.OutputFolder,draw_ib + "\\")
        os.makedirs(draw_ib_config.DrawIBOutputFolder)

        draw_ib_config.VertexLimitHash = fadata.filter_filename(trianglelist_extract_index + "-vb0",".buf")[0][11:19]

        gametype = global_config.D3D11GameTypeConfig.GameTypeName_D3D11GameType_Dict[matched_game_type]
        
        category_hash_dict = {}
        category_filename_dict = {}
        for category_name,category_slot in gametype.CategoryExtractSlotDict:
            category_extract_technique = gametype.CategoryExtractTechniqueDict[category_name]

            extract_index = trianglelist_extract_index
            if category_extract_technique == "pointlist":
                extract_index = pointlist_extract_index

            buf_file_name = fadata.filter_filename(extract_index + "-" + category_slot,".buf")[0]
            category_hash = buf_file_name[11:19]
            category_hash_dict[category_name] = category_hash

            category_read_file_path = os.path.join(fadata.WorkFolder, buf_file_name)
            category_write_filename = draw_ib + "-" + category_name + ".buf"

            category_write_file_path = os.path.join(draw_ib_config.DrawIBOutputFolder, category_write_filename)
            shutil.copy2(category_read_file_path, category_write_file_path)

        draw_ib_config.Category_Hash_Dict = category_hash_dict
        draw_ib_config.Category_FileName_Dict = category_filename_dict

        


        