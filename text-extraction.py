import os
import sys
from lxml import etree
import re


NS = {'a':"http://www.loc.gov/standards/alto/ns-v4#"}  # namespace for the Alto xml


def order_files(dir):
    """Generates a numerically ordered list of file names from the given directory path.

    Returns:
        ordered_files (list): files names from directory ordered by folio number
    """
    # parses file names from a directory (given as an argument in command line) into a list of strings
    file_names = [file for file in os.listdir(dir) if file.endswith(".xml")]
    # extracts the folio number into a list, and orders the list of integers
    folio_numbers = sorted([int(re.search(r"(.*f)(\d+)", file).group(2)) for file in file_names])
    # parses the folio number's prefix: eg. "f" or "document_f"
    prefix = re.search(r"(.*f)(\d+)", file_names[0]).group(1)
    # constructs an ordered list of the complete file names by concatenating the prefix and folio number into a list of strings
    ordered_files = [prefix+str(number)+".xml" for number in folio_numbers]
    return ordered_files


def extract(ordered_files, dir):
    """Extracts text from Alto file's MainZone and puts each TextLine's contents into a list.
        It is possible that a document does not have a @MainZone, @MainZone#1, and/or @MainZone#2.

    Args:
        ordered_files (list): files names from directory ordered by folio number

    Returns:
        text (list): text from every TextLine/String[@CONTENT] that descends from a MainZone <TextBlock>
    """    
    text = []
    for file in ordered_files:
        # parses an xml file (the one currently passed in the loop through the directory's files) and gets the root of the generated etree
        root = etree.parse("{}/{}".format(dir, file)).getroot()

        # searches for the <OtherTag> whose attribute @LABEL equals "MainZone" and returns the value of that tag's attribute @ID
        if root.find('.//a:OtherTag[@LABEL="MainZone"]', namespaces=NS) is not None:
            mainZone_id = root.find('.//a:OtherTag[@LABEL="MainZone"]', namespaces=NS).get("ID")
            # gets a list of @CONTENT's values for every child <String> of every MainZone <TextBlock>
            mainZone_lines = [string.get("CONTENT") for string in root.findall('.//a:TextBlock[@TAGREFS="{}"]/a:TextLine/a:String'.format(mainZone_id), namespaces=NS)]
            text.extend(mainZone_lines)

        # searches for the <OtherTag> whose attribute @LABEL equals "MainZone#1" and returns the value of that tag's attribute @ID
        if root.find('.//a:OtherTag[@LABEL="MainZone#1"]', namespaces=NS) is not None:
            mainZone1_id = root.find('.//a:OtherTag[@LABEL="MainZone#1"]', namespaces=NS).get("ID")
            # gets a list of @CONTENT's values for every child <String> of every MainZone#1 <TextBlock>
            mainZone1_lines = [string.get("CONTENT") for string in root.findall('.//a:TextBlock[@TAGREFS="{}"]/a:TextLine/a:String'.format(mainZone1_id), namespaces=NS)]
            text.extend(mainZone1_lines)

        # searches for the <OtherTag> whose attribute @LABEL equals "MainZone#2" and returns the value of that tag's attribute @ID
        if root.find('.//a:OtherTag[@LABEL="MainZone#2"]', namespaces=NS) is not None:
            mainZone2_id = root.find('.//a:OtherTag[@LABEL="MainZone#2"]', namespaces=NS).get("ID")
            # gets a list of @CONTENT's values for every child <String> of every MainZone#2 <TextBlock>
            mainZone2_lines = [string.get("CONTENT") for string in root.findall('.//a:TextBlock[@TAGREFS="{}"]/a:TextLine/a:String'.format(mainZone2_id), namespaces=NS)]
            text.extend(mainZone2_lines)

    return text


def dump(text, directory):
    """Formats a text according to the needs of the lemmatisation team.

    Args:
        text (list): lines of text from a document's MainZone
    """    
    # string all the lines together
    s = " ".join(text)
    # join words broken by a ¬ or -
    lines = re.sub(r"[¬|\-]\s+", r"", s)
    # jump to new line if "Et" appears not at beginning of new line
    lines = re.sub(r"((?<!^)(?:Et)(\s))", r"\n\n\1", lines)
    # jump to new line if a period is followed by a space and then a capital
    lines = re.sub(r"(\.)(\s)([A-ZÉÀ1-9])", r"\1\n\n\3", lines)
    # jump to new line if a period is followed by a lowercase coordinating conjunction
    lines = re.sub(r"(\.)(\s)(et|car|ou|donc|mais|ni)", r"\1\n\n\3", lines)
    # jump to a new line if one of the following punctuations is present [;!?:]
    lines = re.sub(r"([\;\!\?\:])(\s)", r"\1\n\n", lines)
    # start a new line with the character ⁋
    lines = re.sub(r"(?<!^)(⁋)", r"\n\n\1", lines)
    # replace the medieval abbreviation ⁊ with the word "et"
    lines = re.sub(r"⁊", "et", lines)
    with open(os.path.join(os.path.dirname(directory),os.path.basename(directory)+".txt"), "w") as f:
        f.write(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        directories = [path for path in sys.argv[1:] if os.path.isdir(path)]  # create a list of directories in data/
        for directory in directories:
            ordered_files = order_files(directory)
            text = extract(ordered_files, directory)
            dump(text, directory)
    else:
        print("No directory given")
