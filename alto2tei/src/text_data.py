# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to parse and store data from text in the <sourceDoc>.
# -----------------------------------------------------------

from collections import namedtuple
import pandas as pd
import re


class Text:
    def __init__(self, root):
        self.root = root
        self.data = self.line_data()
        self.main = self.extract()

    def line_data(self):
        """Parse contextual and attribute data for each text line and store it in a named tuple.
        Returns:
            data (list of named tuples): list of data for each text line
        """      

        Line = namedtuple("Line", ["id", "n", "text", "line_type", "zone_type", "zone_id", "page_id"])
        data = [Line(
            ln.getparent().get("{http://www.w3.org/XML/1998/namespace}id"),  # @xml:id of the line's zone
            ln.getparent().get("n"),  # line number
            ln.text,  # text content of line
            ln.getparent().get("type"),  # @type of line
            ln.getparent().getparent().get("type"),  # @type of text block zone
            ln.getparent().getparent().get("{http://www.w3.org/XML/1998/namespace}id"),  # @xml:id of text block zone
            ln.getparent().getparent().getparent().get("{http://www.w3.org/XML/1998/namespace}id"),  # @xml:id of page
        ) for ln in self.root.findall('.//line')]
        return data

    def extract(self):
        """Extract MainZone text lines and clean data by joining broken words and completing abbreviations.
        Returns:
            s (str): text of entire document
        """        
        
        df = pd.DataFrame(self.data)
        # join the text lines and words broken across line breaks together
        s = "%%".join(df.loc[df["zone_type"]=="MainZone"]["text"])
        s = re.sub(r"⁊", "et", s)
        s = re.sub(r"[¬|\-]%%", "", s)
        s = re.sub(r"%%", " ", s)

        # break up the string into segments small enough for the segmentation model
        # capture a period and space (group 1) before capital letter or ⁋ (group 2)
        s = re.sub(r"(\.\s)([A-ZÉÀ])", r"\g<1>\n\g<2>", s)
        # capture "Et " if it is not preceded by string beginning
        s = re.sub(r"(?<!\n)Et\s|(?<!\n)⁋|(?<!\n)¶",r"\n\g<0>",s)
        s = re.sub(r"(?<!\n);|(?<!\n)\?|(?<!\n)\!|(?<!\n):",r"\g<0>\n", s)
        lines = s.split('\n')
        return lines
        