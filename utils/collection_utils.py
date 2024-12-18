import bpy

class CollectionUtils:

    # Recursive select every object in a collection and it's sub collections.
    @classmethod
    def select_collection_objects(cls,collection):
        def recurse_collection(col):
            for obj in col.objects:
                obj.select_set(True)
            for subcol in col.children_recursive:
                recurse_collection(subcol)

        recurse_collection(collection)

    @classmethod
    def find_layer_collection(cls,view_layer, collection_name):
        def recursive_search(layer_collections, collection_name):
            for layer_collection in layer_collections:
                if layer_collection.collection.name == collection_name:
                    return layer_collection
                found = recursive_search(layer_collection.children, collection_name)
                if found:
                    return found
            return None

        return recursive_search(view_layer.layer_collection.children, collection_name)

    @classmethod
    def get_collection_properties(cls,collection_name:str):
        # Nico: Blender Gacha: 
        # Can't get collection's property by bpy.context.collection or it's children or any of children's children.
        # Can only get it's property by search it recursively in bpy.context.view_layer  

        # 获取当前活动的视图层
        view_layer = bpy.context.view_layer

        # 查找指定名称的集合
        collection1 = bpy.data.collections.get(collection_name,None)
        
        if not collection1:
            print(f"集合 '{collection_name}' 不存在")
            return None

        # 递归查找集合在当前视图层中的层集合对象
        layer_collection = CollectionUtils.find_layer_collection(view_layer, collection_name)

        if not layer_collection:
            print(f"集合 '{collection_name}' 不在当前视图层中")
            return None

        # 获取集合的实际属性
        hide_viewport = layer_collection.hide_viewport
        exclude = layer_collection.exclude

        return {
            'name': collection1.name,
            'hide_viewport': hide_viewport,
            'exclude': exclude
        }
    
    @classmethod
    def is_collection_visible(cls,collection_name:str):
        collection_property = CollectionUtils.get_collection_properties(collection_name)

        if collection_property is not None:
            if collection_property["hide_viewport"]:
                return False
            else:
                return True
        else:
            return False
    
    @classmethod
    # get_collection_name_without_default_suffix
    def get_clean_collection_name(cls,collection_name:str):
        if "." in collection_name:
            new_collection_name = collection_name.split(".")[0]
            return new_collection_name
        else:
            return collection_name
        

