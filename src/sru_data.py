# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to parse and store data from the BNF's general catalogue.
# -----------------------------------------------------------

from lxml import etree
import requests
import re

NS = {"s":"http://www.loc.gov/zing/srw/", "m":"info:lc/xmlns/marcxchange-v2"}


class SRU_API:
    def __init__(self, ark):
        """Args:
            ark (string): document ARK in BnF catalogue"""
        self.ark = ark

    def request(self):
            """Request metadata from the BnF's SRU API.
            Returns:
                root (etree_Element): parsed XML tree of requested Unimarc data
                perfect_match (boolean): True if request was completed with Gallica ark / directory basename
            """    

            print("|        requesting data from BnF's SRU API")
            r = requests.get(f'http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=(bib.persistentid all "{self.ark}")')
            root = etree.fromstring(r.content)
            if root.find('.//s:numberOfRecords', namespaces=NS).text=="0":
                perfect_match = False
                print(f"|        \33[31mdid not find digitised document in BnF catalogue\x1b[0m")
            else:
                perfect_match = True
                print(f"|        \33[32mfound digitised document in BnF catalogue\x1b[0m")
            return root, perfect_match

    def author_data(self, author_element, count):
        """Create and fill datafields for relevant author data.
        Args:
            author_element (etree_Element): <mxc: datafield> being parsed
            count (int): author's count in processing
        Returns:
            data (dict) : relevant authorship data (isni, surname, forename, xml:id)
        """        

        # create and set defaults for author data
        fields = ["isni", "primary_name", "secondary_name", "namelink" , "xmlid"]
        data = {}
        {data.setdefault(f, None) for f in fields}
        
        # -- identifier (700s subfield "o") --
        has_isni = author_element.find('m:subfield[@code="o"]', namespaces=NS)
        if has_isni is not None and has_isni.text[0:4]=="ISNI":
            data["isni"] = has_isni.text[4:]

        # -- primary name (700s subfield "a") --
        has_primaryname = author_element.find('m:subfield[@code="a"]', namespaces=NS)
        if has_primaryname is not None:
            data["primary_name"] = has_primaryname.text

        # -- secondary name (700s subfield "b") --
        has_secondaryname = author_element.find('m:subfield[@code="b"]', namespaces=NS)
        if has_secondaryname is not None:
            x = re.search(r"(?:van der)|(?:de la)|(?:de)|(?:du)|(?:von)|(?:van)", has_secondaryname.text)
            if x:
                data["namelink"] = x.group(0)
            y = re.sub(r"(?:van der)|(?:de la)|(?:de)|(?:du)|(?:von)|(?:van)","", has_secondaryname.text)
            if y != "":
                data["secondary_name"] = y

        # -- unique xml:id for the author --
        if data["primary_name"]:
            name = data["primary_name"]
            data["xmlid"] = f"{name[:2]}{count}"
        elif data["secondary_name"]:
            data["xmlid"] = f"{name[:2]}{count}"
        else:
            data["xmlid"] = f"au{count}"
        
        return data
    
    def clean(self, root, perfect_match):
        """Parse and clean data from SRU API response.
        Returns:
            data (dict): all relevant metadata from BnF catalogue
        """      

        # create and set defaults for data
        fields = ["authors", "title", "ptr", "pubplace", "pubplace_key", "publisher", "date", "when", "date_cert", "date_resp", "country", "idno", "objectdesc", "lang"]
        data = {}
        {data.setdefault(f, None) for f in fields}

        if not perfect_match:
            data["found"]=False

        else:
            data["found"]=True
            # enter author data into data dictionary
            data["authors"] = self.clean_authors(root)

            # enter link to the work in the institution's catalogue
            has_ptr = root.find('.//m:controlfield[@tag="003"]', namespaces=NS)
            if has_ptr is not None:
                data["ptr"] = has_ptr.text
            
            # enter date of publication
            has_date_100 = root.find('.//m:datafield[@tag="100"]/m:subfield[@code="a"]', namespaces=NS)
            if has_date_100 is not None and has_date_100.text[8]!="u":
                data["date"] = has_date_100.text[9:13]
                data["when"] = has_date_100.text[9:13]
                data["date_cert"] = self.date_cert(has_date_100.text[8])
                data["date_resp"] = "BNF"
            else:
                has_date_210 = root.find('.//m:datafield[@tag="210"]/m:subfield[@code="d"]', namespaces=NS)
                if has_date_210 is not None:
                    data["date"] = has_date_210.text
            
            
            # enter language of document
            has_lang = root.find('.//m:datafield[@tag="101"]/m:subfield[@code="a"]', namespaces=NS)
            if has_lang is not None:
                data["lang"] = has_lang.text

            # enter country code of publication place
            has_place_key = root.find('.//m:datafield[@tag="102"]/m:subfield[@code="a"]', namespaces=NS)
            if has_place_key is not None:
                data["pubplace_key"] = has_place_key.text

            # enter cleaned title
            has_title = root.find('.//m:datafield[@tag="200"]/m:subfield[@code="a"]', namespaces=NS)
            if has_title is not None:
                data["title"] = has_title.text

            # enter type of document (manuscript or print)
            has_objectdesc = root.find('.//m:datafield[@tag="200"]/m:subfield[@code="b"]', namespaces=NS)
            if has_objectdesc is not None:
                data["objectdesc"] = has_objectdesc.text

            # enter publication place
            has_place = root.find('.//m:datafield[@tag="210"]/m:subfield[@code="a"]', namespaces=NS)
            if has_place is not None:
                data["pubplace"] = has_place.text

            # enter publisher
            has_publisher = root.find('.//m:datafield[@tag="210"]/m:subfield[@code="c"]', namespaces=NS)
            if has_publisher is not None:
                data["publisher"] = has_publisher.text   

            # enter country where the document is conserved
            has_country = root.find('.//m:datafield[@tag="801"]/m:subfield[@code="a"]', namespaces=NS)
            if has_country is not None:
                data["country"] = has_country.text

            # enter catalogue number of the document in the insitution
            has_isno = root.find('.//m:datafield[@tag="930"]/m:subfield[@code="a"]', namespaces=NS)
            if has_isno is not None:
                data["idno"] = has_isno.text

        return data

    def date_cert(self, key):
        """Assigns a degree of certainty to the document's publication date.
        """

        # UNIMARC Norms (ca. 2012)
        # a = currently published continuing resource
        # b = continuing resource no longer being published
        # c = continuing resource of unknown status
        # d = monograph complete when issued, or issued within one calendar year
        # e = reproduction of a document
        # f = monograh, date of publication uncertain
        # g = mongraph whose publication continues for more than a year
        # h = monograph with both actual and copyright/privilege date
        # i = monograph with both release/issue date and production date
        # j = document with detailed date of production
        # k = monograph published in a certain year and printed in a different year
        # u = dates of publication unkonwn
        if key == "a" or key == "b" or key == "d" or key == "e" or key == "h" or key == "i" or key == "j":
            degree = "high"
        if key == "g" or key == "k":
            degree = "medium"
        if key == "f":
            degree = "low"
        return degree

    def clean_authors(self, root):
        """Parses and cleans author data from Unimarc fields 700 and/or 701.
        Returns:
            authors (dict): relevant authorship data (isni, surname, forename, xml:id)
        """     
           
        authors = []
        count = 0
        if root.find('.//m:datafield[@tag="700"]', namespaces=NS) is not None:
            # datafield 700 is not repeatable
            author_element = root.find('.//m:datafield[@tag="700"]', namespaces=NS)
            count+=1
            authors.append(self.author_data(author_element, count))
        if root.find('.//m:datafield[@tag="701"]', namespaces=NS) is not None:
            # datafield 701 is repeatable
            author_elements = root.findall('.//m:datafield[@tag="701"]', namespaces=NS)
            for element in author_elements:
                count+=1
                authors.append(self.author_data(element, count))
        return authors

