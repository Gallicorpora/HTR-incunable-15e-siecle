# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to build elements inside the <sourceDoc> and map data to them.
# -----------------------------------------------------------

from lxml import etree
import re

NS = {'a':"http://www.loc.gov/standards/alto/ns-v4#"}  # namespace for the Alto xml


class SurfaceTree:
    """Creates a <surface> element and its children for one page (ALTO file) of a document.
    """    
    
    def __init__(self, doc, folio, alto_root):
        self.doc = doc
        self.folio = folio
        self.root = alto_root

    def surface(self, surface_group, page_attributes):
        # -- surfaceGrp/surface-- 
        surface = etree.SubElement(surface_group, "surface", page_attributes)
        # create <graphic> and assign its attributes
        etree.SubElement(surface, "graphic", url=f"https://gallica.bnf.fr/iiif/ark:/12148/{self.doc}/f{self.folio}/full/full/0/native.jpg")
        return surface

    def zone1(self, surface, textblock_atts, textblock_count):
        # -- surfaceGrp/surface/zone -- 
        xml_id = {"{http://www.w3.org/XML/1998/namespace}id":f"f{self.folio}_z{textblock_count+1}"}
        text_block = etree.SubElement(surface, "zone", xml_id)
        for k,v in textblock_atts[textblock_count].items():
            text_block.attrib[k]=v
        return text_block

    def zone2(self, lines_on_page, text_block, textblock_count, textline_atts, textline_count, processed_textline):    
        # -- surfaceGrp/surface/zone/zone --           
        zone_id = {"{http://www.w3.org/XML/1998/namespace}id":f"f{self.folio}_z{textblock_count+1}_l{textline_count+1}"}
        text_line = etree.SubElement(text_block, "zone", zone_id)
        for k,v in textline_atts[textline_count].items():
            text_line.attrib[k]=v
        text_line.attrib["n"]=str(lines_on_page)
        # -- surfaceGrp/surface/zone/zone --
        path_id = {"{http://www.w3.org/XML/1998/namespace}id":f"f{self.folio}_z{textblock_count+1}_l{textline_count+1}_p"}
        baseline = etree.SubElement(text_line, "path", path_id)
        b = self.root.find(f'.//a:TextLine[@ID="{processed_textline}"]', namespaces=NS).get("BASELINE")
        baseline.attrib["points"] = " ".join([re.sub(r"\s", ",", x) for x in re.findall(r"(\d+ \d+)", b)])
        return text_line

    def line(self, text_line, textblock_count, textline_count, processed_textline):
        # -- surfaceGrp/surface/zone/zone/line -- 
        xml_id = {"{http://www.w3.org/XML/1998/namespace}id":f"f{self.folio}_z{textblock_count+1}_l{textline_count+1}_t"}
        string = etree.SubElement(text_line, "line", xml_id)
        string.text = self.root.find(f'.//a:TextLine[@ID="{processed_textline}"]/a:String', namespaces=NS).get("CONTENT")
        return string
        