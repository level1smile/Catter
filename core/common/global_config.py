import os
import re

from dataclasses import dataclass, field
from typing import List,Dict
from enum import Enum

from ..utils.dbmt_file_utils import *
from ..utils.dbmt_log_utils import *

from .d3d11_game_type import *
from .frame_analysis import *


@dataclass
class DrawIBConfig:
    DrawIB:str
    GameTypeName:str
    
    ImportModelList:list[str] = field(init=False)
    VertexLimitHash:str = field(init=False)
    DrawIBOutputFolder:str = field(init=False)

    Category_FileName_Dict:Dict[str,str] =  field(init=False)
    Category_Hash_Dict:Dict[str,str] = field(init=False)
    MatchFirstIndex_PartName_Dict:Dict[str,str] = field(init=False)

    def __post_init__(self):
        self.Category_FileName_Dict = {}
        self.Category_Hash_Dict = {}
        self.MatchFirstIndex_PartName_Dict = {}


@dataclass
class GlobalConfig:
    # We put all loader in a fixed folder structure so can locate them only by game name.
    GameName:str
    # This folder contains all 3dmigoto loader seperated by game name.
    GameLoaderPath:str
    # This folder contains all config json file.
    ConfigFolderPath:str

    # Where 3Dmigoto's d3d11.dll located.
    LoaderFolder:str = field(init=False)
    # eg: FrameAnalysis-2024-10-30-114032.
    FrameAnalysisFolder:str = field(init=False)
    # path of 3Dmigoto's d3d11.dll located folder + current work frame analysis folder.
    WorkFolder:str = field(init=False)
    # deduped folder path of current frame analysis folder.
    DedupedFolder:str = field(init=False)
    # output folder
    OutputFolder:str = field(init=False)

    # wrapper config for all d3d11 game type.
    D3D11GameTypeConfig:D3D11GameTypeLv2 = field(init=False,repr=False)

    FAData:FrameAnalysisData = field(init=False,repr=False)
    FALog:FrameAnalysisLog = field(init=False,repr=False)

    def __post_init__(self):
        self.initialize_folder_path()
        self.initialize_d3d11_gametype()

    def initialize_folder_path(self):
        self.LoaderFolder = os.path.join(self.GameLoaderPath,self.GameName + "\\3Dmigoto\\")
        if not os.path.exists(self.LoaderFolder):
            log_warning_str("LoaderFolder doesn't exists. " + self.LoaderFolder)

        self.FrameAnalysisFolder = self.find_latest_frameanalysis_folder()
        if self.FrameAnalysisFolder == "":
            log_warning_str("Latest FrameAnalysis folder not found. WorkFolder will not exists.")
        else:
            self.WorkFolder = os.path.join(self.LoaderFolder, self.FrameAnalysisFolder + "\\") 
            log_info("Current WorkFolder: " + self.WorkFolder)

            self.DedupedFolder =os.path.join(self.WorkFolder, "deduped\\")
            if not os.path.exists(self.DedupedFolder):
                log_warning_str("Current DedupedFolder not exists: " + self.DedupedFolder)
            
            self.FAData = FrameAnalysisData(WorkFolder=self.WorkFolder)
            self.FALog = FrameAnalysisLog(WorkFolder=self.WorkFolder)
        self.OutputFolder = os.path.join(self.LoaderFolder,"Mods\\output\\")
        # Create output folder.
        os.makedirs(self.OutputFolder)

    def find_latest_frameanalysis_folder(self):
        frame_analysis_folder_list = []

        # return default "" if the LoaderFolder not exists.
        if not os.path.exists(self.LoaderFolder):
            return ""
        
        folder_list = os.listdir(self.LoaderFolder)
        for folder_name in folder_list:
            if "FrameAnalysis-" in folder_name:
                frame_analysis_folder_list.append(folder_name)
            
        frame_analysis_folder_list.sort(reverse=True)
        if len(frame_analysis_folder_list) != 0:
            return frame_analysis_folder_list[0]
        else:
            return ""

    def initialize_d3d11_gametype(self):
        self.D3D11GameTypeConfig = D3D11GameTypeLv2(GameTypeConfigFolderPath=self.ConfigFolderPath)
