import json

class JsonUtils:


    @classmethod
    def SaveToFile(cls,filepath:str,json_dict:dict):
        # 将字典转换为 JSON 格式的字符串
        json_string = json.dumps(json_dict, ensure_ascii=False, indent=4)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_string)
