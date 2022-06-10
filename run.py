from collections import namedtuple
from pathlib import Path
#from datetime import datetime
from time import perf_counter

import yaml

from src.build import XMLTEI
from src.write_output import Write


# from the project's configuration YAML, parse where it says to find the ALTO files' directories
with open("alto2tei/src/config.yml") as cf_file:
        config = yaml.safe_load(cf_file.read())
        p = Path(config.get(("data"))["path"])

# for every directory in the path indicated in the config YAML,
# get the directory's name (str) and the paths of its ALTO files (os.path)
Docs = namedtuple("Docs", ["doc_name", "filepaths"])
docs = [Docs    (d.name,                                      # name of document folder
                [f for f in d.iterdir() if f.suffix==".xml"]) # relative filepath for file
        for d in p.iterdir() if d.is_dir()]

# process each directory in path "p"
for d in docs:
    # instantiate the class XMLTEI for the current document in the loop
    x = XMLTEI(d.doc_name, d.filepaths)
    print("\n=====================================")
    print(f"\33[32m~ now processing document {d.doc_name} ~\x1b[0m")

    # -- phase 1 -- metadata preparation
    print(f"\33[33mmapping metadata\x1b[0m")
    t0 = perf_counter()
    # perform the method .prepare_data() on this document's XMLTEI instance
    # this method parses and cleans metadata unique to this document
    x.prepare_data()
    print("|________finished in {:.4f} seconds".format(perf_counter() - t0))

    # -- phase 2 -- XML-TEI construction
    print(f"\33[33mcreating <teiHeader> and <sourceDoc>\x1b[0m")
    t0 = perf_counter()
    # perform the method .build_tree() on this document's XMLTEI instance
    # this method constructs the XML-TEI elements <teiHeader> and <sourceDoc>
    x.build_tree()
    print("|________finished in {:.4f} seconds".format(perf_counter() - t0))

    # -- phase 3 -- extract and annotate text in <body> and <standOff>
    print(f"\33[33mextracting and annotating text in <body>\x1b[0m")
    t0 = perf_counter()
    # perform the method .annotate_body() on this document's XMLTEI instance
    # this method extracts text from the <sourceDoc> and maps it to XML-TEI elements in <body>
    root = x.annotate_text()
    print("|________finished in {:.4f} seconds".format(perf_counter() - t0))

    # -- output XML-TEI file --
    Write(d.doc_name, x.root).write()
