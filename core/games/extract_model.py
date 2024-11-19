from ..common.global_config import *

def unity_auto_gametype(draw_ib:str,global_config:GlobalConfig):
    # auto detect game type
    for gametype in global_config.D3D11GameTypeConfig.Ordered_GPU_CPU_D3D11GameTypeList:

        # find TEXCOORD category
        texcoord_category = gametype.ElementNameD3D11ElementDict["TEXCOORD"].Category
        texcoord_slot = gametype.CategoryExtractSlotDict[texcoord_category]
        texcoord_stride = gametype.CategoryStrideDict[texcoord_category]

                

    
def unity_extract_model(draw_ib_list,global_config:GlobalConfig):
    log_info("Start to extract model:")
    for draw_ib in draw_ib_list:
        log_info("Current DrawIB: " + draw_ib)

        gametype = unity_auto_gametype(draw_ib=draw_ib,global_config=global_config)

        # Find Trianglelist Index from FALog
        falog = FrameAnalysisLog(global_config.WorkFolder)
        trianglelist_index_list= falog.get_index_list_by_draw_ib(draw_ib=draw_ib,only_match_first=False)
        for trianglelist_index in trianglelist_index_list:
            log_info("Index: " + trianglelist_index)
            