# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to parse the attributes of the <sourceDoc>'s elements.
# -----------------------------------------------------------

from lxml import etree
import re

NS = {'a':"http://www.loc.gov/standards/alto/ns-v4#"}  # namespace for the Alto xml


class Attributes:
    def __init__(self, doc, folio, alto_root, tags):
        self.doc = doc
        self.folio = folio
        self.root = alto_root
        self.tags = tags

    def surface(self):
        """Create attributes for the TEI <surface> element using data parsed from the ALTO file's <Page> element.
            The TEI attributes for <surface> are: @n (page number), 
                                                @ulx (upper left x-axis pixel position, always 0), 
                                                @uly (upper left y-axis pixel position, always 0), 
                                                @lrx (lower right x-axis pixel position = width of page), 
                                                @lry (lower right y-axis pixel position = length of page)
        Returns:
            attributes (dict): dictionary of attribute names and their values
        """    

        # create a dictionary of attributes names and their values for the ALTO file's <Page> element
        att_list = self.root.find('.//a:Page', namespaces=NS).attrib
        # assign the ALTO file's extracted <Page> attribute values to TEI attribute names
        attributes = {"{http://www.w3.org/XML/1998/namespace}id":f"f{self.folio}",
                    "n":att_list["PHYSICAL_IMG_NR"],
                    "ulx":"0",
                    "uly":"0",
                    "lrx":att_list["WIDTH"],
                    "lry":att_list["HEIGHT"]}
        return attributes

    def zone(self, parent, target):
        """Create attributes for one of the two types of TEI <zone> elements: (a) TextBlock and (b) TextLine.

        Args:
            parent (str): parent's entity name and @ID in the ALTO file for the entity being transformed into a <zone>, followed by a '/'
                            eg. 'TextBlock[@ID="eSc_textblock_20c2f4d8"]/'
            target (str): entity name in the ALTO file for the entity being transformed into a <zone>
                            eg. 'TextLine'
        Returns:
            attributes (list): list of dictionaries {attribute name (str): value (str)}
            processed_blocks (list): IDs of the elements whose data were extracted
        """        
        
        # create a list of all etree_Elements in the ALTO file targeted for transformation into a <zone>
        zone_elements = [z for z in self.root.findall(f'.//a:{parent}a:{target}', namespaces=NS) \
                        if 'TAGREFS' in z.attrib and\
                        z.attrib['TAGREFS']!="BT" \
                        and z.attrib['TAGREFS']!="LT"]
                        # these conditions ignore any zone-like element whose tag is invalid or which is missing @TAGREFS
        # create a list whose items are dictionaries naming each targeted ALTO element's attributes
        att_list = [z.attrib for z in zone_elements]
        # extract the attributes for the child <Polygon> of each targeted ALTO element and put that dictionary into a list
        points = [z.find('.//a:Polygon', namespaces=NS).attrib for z in zone_elements]

        attributes = []
        processed_blocks = []

        # run through each targeted ALTO element one by one
        for i in range(len(zone_elements)):
            # parse the three (possible) components of the targeted ALTO element's @TAGREFS, according to SegmOnto guidelines;
            # the 3 groups of this regex parse the following expected tag syntax: MainZone:column#1 --> (MainZone)(column)(1)
            tag_parts = re.match(r"(\w+):?(\w+)?#?(\d?)?", str(self.tags[att_list[i]["TAGREFS"]]))

            # specifically for the current targeted ALTO element [i], reformat the attribute values extracted 
            # from its child <Polygon> (see above, stored in variable "points") so that every second value 
            # is joined to the previous value by a comma; eg. "2204 4621 2190 4528" --> "2204,4621 2190,4528"
            zone_points = " ".join([re.sub(r"\s", ",", x) for x in re.findall(r"(\d+ \d+)", points[i]["POINTS"])])

            # for the current targeted ALTO element [i], extract the values of the attributes related to coordinates
            x = att_list[i]["HPOS"]
            y = att_list[i]["VPOS"]
            w = att_list[i]["WIDTH"]
            h = att_list[i]["HEIGHT"]

            # assign together the newly created/formatted attribute values to TEI attribute names that the <zone> will use
            zone_att = {
                "type":tag_parts.group(1),
                "subtype":tag_parts.group(2) or "none",
                "n":tag_parts.group(3) or "none",
                "points":zone_points,
                # use the values of the ALTO element's @HPOS, @VPOS, @WIDTH, @HEIGHT to complete region parameters for the IIIF Image API URI
                "source":f"https://gallica.bnf.fr/iiif/ark:/12148/{self.doc}/f{self.folio}/{x},{y},{w},{h}/full/0/native.jpg"
            }

            # update a list of TEI attribute-value pairs with those parsed from the current targeted ALTO element
            attributes.append(zone_att)

            # update a list of @IDs from all the ALTO elements that this method has processed;
            # the IDs in this list will help create the "parent" parameter for nested zones, i.e. TextLine, 
            # whose parent is always a TextBlock, eg. the first <TextLine> of a <TextBlock> would hvae the parent: 
            # f'TextBlock[@ID="{processed_blocks[0]}"]/'
            processed_blocks.append(att_list[i]["ID"])

        return attributes, processed_blocks