

# Recursive select every object in a collection and it's sub collections.
def select_collection_objects(collection):
    def recurse_collection(col):
        for obj in col.objects:
            obj.select_set(True)
        for subcol in col.children_recursive:
            recurse_collection(subcol)

    recurse_collection(collection)

