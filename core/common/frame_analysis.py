from dataclasses import dataclass, field
from typing import List,Dict
from enum import Enum

from ..utils.dbmt_file_utils import *
from ..utils.dbmt_log_utils import *

# Nico: Thanks for SpectrumQT's WWMI project, I learned how to use @dataclass to save my time 
# and lots of other python features so use python can works as good as C++ and better and faster.

class HashType(Enum):
    Texture = "-ps-t"
    VertexBuffer = "-vb"
    ConstantBuffer = "-cb"

    ComputeShader = "-cs="
    VertexShader = "-vs="
    PixelShader = "-ps="


@dataclass
class ResourceFile:
    FilePath:str

    FileName:str = field(init=False)
    TypeSlot:str = field(init=False)

    def __post_init__(self):
        self.FileName = os.path.basename(self.FilePath)
        self.TypeSlot = self.get_type_slot()

    def get_hash(self,hash_type:str,hash_length:int)->str:
        if hash_type not in self.FileName:
            return ""
            
        if "=" in hash_type:
            split_right_str = self.FileName.split(hash_type)[1]
            return split_right_str[0:hash_length]
        else:
            split_right_str = self.FileName.split(hash_type)[1]
            equal_index = split_right_str.find('=')
            start_index = equal_index + 1
            end_index = equal_index + hash_length
            return split_right_str[start_index:end_index]
        
    def get_type_slot(self)->str:
        if "=" in self.FileName:
            split_first = self.FileName.split("=")[0]

        return split_first[len("000001-"):]

@dataclass
class LogCommand:
    LogLine:str

    CallIndex:str = field(init=False)
    ArgumentKVMap:Dict[str,str] = field(init=False)

    def __post_init__(self):
        self.CallIndex = self.LogLine[0:6]
        self.ArgumentKVMap = {}

        start_index = self.LogLine.find("(") + 1
        end_index = self.LogLine.find(")")
        arguments = self.LogLine[start_index: end_index]
        arguments_split = arguments.split(",")
        for argument_str in arguments_split:
            trim_argument = argument_str.strip()
            kvlist = trim_argument.split(":")
            self.ArgumentKVMap[kvlist[0]] = kvlist[1]
        

@dataclass
class IASetVertexBuffers:
    LogLine:str

    CallIndex:str = field(init=False)
    StartSlot:int  = field(init=False)
    NumBuffers:int = field(init=False)
    ppVertexBuffers:str = field(init=False)
    ppStrides:str = field(init=False)
    pOffsets:str = field(init=False)

    def __post_init__(self):
        log_command = LogCommand(LogLine=self.LogLine)
        self.CallIndex = log_command.CallIndex

        if "StartSlot" in log_command.ArgumentKVMap:
            self.StartSlot = int(log_command.ArgumentKVMap["StartSlot"])
        elif "NumBuffers" in log_command.ArgumentKVMap:
            self.NumBuffers = int(log_command.ArgumentKVMap["NumBuffers"])
        elif "ppVertexBuffers" in log_command.ArgumentKVMap:
            self.ppVertexBuffers = log_command.ArgumentKVMap["ppVertexBuffers"]
        elif "ppStrides" in log_command.ArgumentKVMap:
            self.ppStrides = log_command.ArgumentKVMap["ppStrides"]
        elif "pOffsets" in log_command.ArgumentKVMap:
            self.pOffsets = log_command.ArgumentKVMap["pOffsets"]


@dataclass
class ShaderResource:
    LogLine:str

    Index:str = field(init=False)
    Resource:str = field(init=False)
    View:str = field(init=False)
    Hash:str = field(init=False)

    def __post_init__(self):
        trim_log_line = self.LogLine.strip()
        splits = trim_log_line.split(":")
        self.Index = splits[0]

        arguments_splits = splits[1].strip().split(" ")

        for kv in arguments_splits:
            kvlist = kv.split("=")
            key = kvlist[0].strip()
            value = kvlist[1].strip()

            if key == "resource":
                self.Resource = value
            elif key == "hash":
                self.Hash = value
            elif key == "view":
                self.View = value


@dataclass
class FrameAnalysisData:
    WorkFolder:str

    FileNameList:list[str] = field(init=False)
    DedupedFileNameList:list[str] = field(init=False)

    def __post_init__(self):
        self.FileNameList = dbmt_fileutil__list_files(self.WorkFolder)
        self.DedupedFileNameList = dbmt_fileutil__list_files(os.path.join(self.WorkFolder,"deduped\\"))

    def filter_filename(self,contain:str,suffix:str) -> list[str]:
        new_filename_list = []
        for file_name in self.FileNameList:
            if contain in file_name and file_name.endswith(suffix):
                new_filename_list.append(file_name)
        return new_filename_list
    
    def get_indexlist_by_drawib(self,drawib:str) -> list[str]:
        indexlist = []
        ib_related_filename_list = self.filter_filename(contain=drawib,suffix=".buf")
        for ib_related_filename in ib_related_filename_list:
            indexlist.append(ib_related_filename[0:6])
        return indexlist
    
    def get_deduped_filename_by_hash(self,file_hash:str)->str:
        for deduped_filename in self.DedupedFileNameList:
            if file_hash in deduped_filename:
                return deduped_filename
        return ""
    
    def get_trianglelist_index_list(self,draw_ib:str)->list[str]:
        for filename in self.FileNameList:
            if not filename.endswith(".txt"):
                continue
            
            if draw_ib in filename:
                ib_txt_file = ""
                # TODO 




@dataclass
class FrameAnalysisLog:
    WorkFolder:str

    LogFilePath:str = field(init=False)

    LogLineList:list[str] = field(init=False)

    def __post_init__(self):
        self.LogFilePath = os.path.join(self.WorkFolder,"log.txt")
        with open(self.LogFilePath, 'r') as file:
            self.LogLineList = file.readlines()
    
    def get_index_list_by_draw_ib(self,draw_ib:str,only_match_first:bool)->list[str]:
        index_set = set()
        current_index = ""
        for log_line in self.LogLineList:
            if log_line.startswith("00"):
                current_index = log_line[0:6]
            
            if "hash=" + draw_ib in log_line:
                index_set.add(current_index)
                if only_match_first:
                    break
        index_list = list(index_set)
        index_list.sort()
        return index_list


    def get_pointlist_index_by_draw_ib(self,draw_ib:str)->str:
        first_trianglelist_index = self.get_index_list_by_draw_ib(draw_ib=draw_ib,only_match_first=True)[0]
        trianglelist_indexline_list = self.get_linelist_by_index(index=first_trianglelist_index)
        vb0_hash = ""
        find_ia_set_vb = False
        for line in trianglelist_indexline_list:
            if "IASetVertexBuffers" in line:
                iasetvb = IASetVertexBuffers(LogLine=line)
                find_ia_set_vb = True
                continue

            if find_ia_set_vb:
                if not line.startswith("00"):

                    ia_resource = ShaderResource(LogLine=line)
                    if "vb"+ia_resource.Index == "vb0":
                        vb0_hash = ia_resource.Hash

                else:
                    break
        if vb0_hash == "":
            return ""
        
        findstr = "hash=" + vb0_hash
        current_index = ""
        trianglelist_index_number = int(first_trianglelist_index)
        for line in self.LogLineList:
            if line.startswith("00"):
                current_index = line[0:6]
            
            if findstr in line:
                pointlist_index_number = int(current_index)
                if pointlist_index_number < trianglelist_index_number:
                    return current_index
                else:
                    return ""

        return ""

    def get_linelist_by_index(self,index:str)->list[str]:
        index_line_list = []
        index_number = int(index)
        find_index = False
        for log_line in self.LogLineList:
            if log_line.startswith("00") and not find_index:
                current_index_number = int(log_line[0:6])
                if index_number == current_index_number:
                    find_index = True
                    index_line_list.append(log_line)
                    continue
            
            if find_index:
                if log_line.startswith("00"):
                    current_index_number = int(log_line[0:6])
                    if current_index_number > index_number:
                        break
                    else:
                        index_line_list.append(log_line)
                else:
                    index_line_list.append(log_line)

        return index_line_list
