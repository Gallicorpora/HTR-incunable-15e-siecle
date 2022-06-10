# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python script to insert text segments into a TEI file's <standOff>.
# -----------------------------------------------------------

from lxml import etree

def segment(root, text):
    standoff = etree.SubElement(root, "standOff")
    for n,i in enumerate(text):
        seg = etree.Element("seg")
        seg.text = i
        seg.attrib["n"] = str(n+1)
        seg.attrib["{http://www.w3.org/XML/1998/namespace}id"] = "s" + seg.get("n")
        standoff.append(seg)