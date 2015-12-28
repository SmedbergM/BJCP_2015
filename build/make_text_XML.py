"""Script to build XML version of any text section (non-beer-style)
of the BJCP 2015 guidelines."""

from lxml import etree
import re

secpat = r"(#+)\s*(.+)"

def build_xml(root_node, mdfname):
    point = root_node
    with open(mdfname, encoding = 'utf8') as md:
        for line in md:
            line = line.strip()
            if line:
                m = re.match(secpat,line)
                if m:
                    while len(m.group(1)) <= int(point.attrib.get("level","0")):
                        point = point.getparent()
                    point = etree.SubElement(point,"section", level = "{0}".format(len(m.group(1))), title = m.group(2))
                elif "|" in line:
                    point.append(parse_table(line,md))
                else:
                    par = etree.SubElement(point,"paragraph")
                    par.text = line                

def parse_table(header,line_iterator):
    cols = [c.strip() for c in header.split('|')[1:]]
    line = next(line_iterator) # skip alignment line
    tableNode = etree.Element('table')
    try:
        while '|' in line:
            line = next(line_iterator)
            vals = [v.strip() for v in line.split('|')[1:]]
            etree.SubElement(tableNode,'row',attrib = dict(zip(cols,vals)))
    except StopIteration:
        pass
    return tableNode

if __name__ == "__main__":
    from sys import argv

    DocNode = etree.Element('doc')
    DocTree = etree.ElementTree(DocNode)

    MDfname = argv[1]
    if len(argv) > 2:
        XMLfname = argv[2]
    else:
        XMLfname = re.sub("\.md",".xml",
                     re.sub("md/","xml/",MDfname))

    build_xml(DocNode, MDfname)

    DocTree.write(XMLfname, pretty_print = True, encoding = 'utf8')
