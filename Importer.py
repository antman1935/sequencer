import os
import importlib

class Importer:
    dirname = os.path.dirname(__file__)

    def importSubdirectory(relPath: str):
        parts = relPath.split("/")
        subdir = os.path.join(Importer.dirname, *parts)

        for filename in os.listdir(subdir):
            name = filename.split(".")
            print(name)
            if len(name) != 2 or name[1] != "py":
                continue

            module_name = ".".join(parts + [name[0]])
            print("importing", module_name)
            importlib.import_module(module_name)