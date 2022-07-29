# -----------------------------------------------------------
# Code by: Kelly Christensen
# Python class to parse and store data from a document's IIIF manifest.
# -----------------------------------------------------------

import os
import requests
import re


class IIIF:
    def __init__(self, document, iiifURI):
        self.document = document
        self.scheme = iiifURI["scheme"]
        self.server = iiifURI["server"]
        self.manifest_prefix = iiifURI["manifest_prefix"]
        self.manifest_suffix= iiifURI["manifest_suffix"]

    def request(self):
        # Request manifest from the IIIF Presentation API
        r = requests.get(f"{self.scheme}://{self.server}{self.manifest_prefix}{os.path.basename(self.document)}{self.manifest_suffix}")
        try:
            response = {d["label"]:d["value"] for d in r.json()["metadata"]}
        except:
            print("The IIIF manifest was not read correctly.")
            response = {}
        return response

    def clean(self, response):
        """Clean metadata received from Gallica API.
        Returns:
            clean_data (dict): cleaned data from IIIF manifest with values == None if not present in API request
        """      
          
        # Make defaultdict for cleaned metadata
        fields = ["Relation", "Catalogue ARK", "Repository", "Shelfmark", "Title", "Language", "Creator", "Date"]
        clean_data= {}
        {clean_data.setdefault(f, None) for f in fields}
        for k,v in response.items():
            if type(v) is list and list(v[0].keys())[0]=="@value":
                clean_data[k]=v[0]["@value"]
            else:
                clean_data[k]=v
        # Derive catalogue ARK from "Relation" field; this will be used to access the BnF's SRU API
        if clean_data["Relation"] and re.search(r"\/((?:ark:)\/\w+\/\w+)", clean_data["Relation"]):
            clean_data["Catalogue ARK"]=(re.search(r"\/((?:ark:)\/\w+\/\w+)", clean_data["Relation"]).group(1))
        # Clean author name, getting rid of ". Auteur du texte" at the end of the string
        if clean_data["Creator"]:
            clean_data["Creator"]=re.sub(r"(\s\(|\.).+", '', clean_data["Creator"])
        return clean_data