# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to build the architecture of a default <teiHeader>.
# -----------------------------------------------------------

from lxml import etree
from datetime import datetime
from collections import defaultdict
import yaml

class DefaultTree:
    children = defaultdict(list)
    def __init__(self, document, root, metadata, count_pages):
        self.document = document
        self.root = root
        self.sru = metadata["sru"]
        self.iiif = metadata["iiif"]
        self.count = str(count_pages)

    def build(self):
        with open("alto2tei/src/config.yml") as cf_file:
            config = yaml.safe_load(cf_file.read())

        if self.sru["found"]:
            default_text = "Information not available."
            num_authors = len(self.sru["authors"])
        else:
            default_text = "Digitised resource not found in BnF catalogue."
            num_authors = 1  # method of extracting IIIF manifest data will only return 1 author

        teiHeader = etree.SubElement(self.root, "teiHeader")
        fileDesc = etree.SubElement(teiHeader, "fileDesc")
        profileDesc = etree.SubElement(teiHeader, "profileDesc")
        titleStmt = etree.SubElement(fileDesc, "titleStmt")
        self.children["titleStmt"] = titleStmt
        self.children["ts_title"] = etree.SubElement(titleStmt, "title")  # pass to other methods
        self.children["ts_title"].text = default_text
        for i in range(num_authors):
            etree.SubElement(titleStmt, "author")
        if num_authors == 0:
            ts_author = etree.SubElement(titleStmt, "author")
            ts_author.text = default_text
        respStmt = etree.SubElement(titleStmt, "respStmt")
        resp = etree.SubElement(respStmt, "resp")
        resp.text = config["responsibility"]["text"]
        for i in range(len(config["responsibility"]["resp"])):
            persName = etree.SubElement(respStmt, "persName")
            forename = etree.SubElement(persName, "forename")
            forename.text = config["responsibility"]["resp"][i]["forename"]
            surname = etree.SubElement(persName, "surname")
            surname.text = config["responsibility"]["resp"][i]["surname"]
            etree.SubElement(persName, "ptr", config["responsibility"]["resp"][i]["ptr"])
        extent = etree.SubElement(fileDesc, "extent")
        etree.SubElement(extent, "measure", unit="images", n=self.count)
        publicationStmt = etree.SubElement(fileDesc, "publicationStmt")
        publisher = etree.SubElement(publicationStmt, "publisher")
        publisher.text = config["responsibility"]["publisher"]
        authority = etree.SubElement(publicationStmt, "authority")
        authority.text = config["responsibility"]["authority"]
        availability = etree.SubElement(publicationStmt, "availability", config["responsibility"]["availability"])
        etree.SubElement(availability, "licence", config["responsibility"]["licence"])
        today = datetime.today().strftime('%Y-%m-%d')
        etree.SubElement(publicationStmt, "date", when=today)
        sourceDesc = etree.SubElement(fileDesc, "sourceDesc")
        bibl = etree.SubElement(sourceDesc, "bibl")
        self.children["bibl"] = bibl
        self.children["ptr"] = etree.SubElement(bibl, "ptr")  # pass to other methods
        for i in range(num_authors):
            etree.SubElement(bibl, "author")
        if num_authors == 0:
            bib_author = etree.SubElement(bibl, "author")
            bib_author.text = default_text
        self.children["bib_title"] = etree.SubElement(bibl, "title")  # pass to other methods
        self.children["bib_title"].text = default_text
        self.children["pubPlace"] = etree.SubElement(bibl, "pubPlace")  # pass to other methods
        self.children["pubPlace"].text = default_text
        self.children["publisher"] = etree.SubElement(bibl, "publisher")  # pass to other methods
        self.children["publisher"].text = default_text
        self.children["date"] = etree.SubElement(bibl, "date")  # pass to other methods
        self.children["date"].text = default_text
        msDesc = etree.SubElement(sourceDesc, "msDesc")
        msIdentifier = etree.SubElement(msDesc, "msIdentifier")
        self.children["country"] = etree.SubElement(msIdentifier, "country")  # pass to other methods
        self.children["settlement"] = etree.SubElement(msIdentifier, "settlement")  # pass to other methods
        self.children["settlement"].text = default_text
        self.children["repository"] = etree.SubElement(msIdentifier, "repository")  # pass to other methods
        self.children["repository"].text = default_text
        self.children["idno"] = etree.SubElement(msIdentifier, "idno")  # pass to other methods
        self.children["idno"].text = default_text
        altIdentifer = etree.SubElement(msIdentifier, "altIdentifier")
        alt_idno = etree.SubElement(altIdentifer, "idno", type="ark")  # pass to other methods
        alt_idno.text = self.document
        physDesc = etree.SubElement(msDesc, "physDesc")
        objectDesc = etree.SubElement(physDesc, "objectDesc")
        self.children["p"] = etree.SubElement(objectDesc, "p")  # pass to other methods
        self.children["p"].text = default_text
        langUsage = etree.SubElement(profileDesc, "langUsage")
        self.children["language"] = etree.SubElement(langUsage, "language") # pass to other methods
        self.children["language"].attrib["ident"] = ""
