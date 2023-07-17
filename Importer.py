# author: antman1935, anthony.lamont99@yahoo.com

import os
import importlib

class Importer:
    dirname = os.path.dirname(__file__)

    def importSubdirectory(relPath: str):
        parts = relPath.split("/")
        subdir = os.path.join(Importer.dirname, *parts)

        for filename in os.listdir(subdir):
            name = filename.split(".")
            if len(name) != 2 or name[1] != "py":
                continue

            module_name = ".".join(parts + [name[0]])
            importlib.import_module(module_name)