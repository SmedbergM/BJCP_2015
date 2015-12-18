"""Script to build XML version of any text section (non-beer-style)
of the BJCP 2015 guidelines."""

from lxml import etree
import re

secpat = r"(#+)\s*(.+)"

DocNode = etree.Element('doc')
DocTree = etree.ElementTree(DocNode)

def build_xml(root_node, mdfname):
    point = root_node
    with open(mdfname, encoding = 'utf8') as md:
        for line in (line.strip() for line in md if line.strip()):
            m = re.match(secpat,line)
            if m:
                while len(m.group(1)) <= int(point.attrib.get("level","0")):
                    point = point.getparent()
                point = etree.SubElement(point,"section", level = "{0}".format(len(m.group(1))), title = m.group(2))
            else:
                par = etree.SubElement(point,"paragraph")
                par.text = line                

if __name__ == "__main__":
    from sys import argv

    MDfname = argv[1]
    XMLfname = re.sub("\.md",".xml",\
                     re.sub("md/","xml/",MDfname))

    build_xml(DocNode, MDfname)

    DocTree.write(XMLfname, pretty_print = True, encoding = 'utf8')
