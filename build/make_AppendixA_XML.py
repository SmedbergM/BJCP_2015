import re
from lxml import etree

secpat = r"#\s*(.*)\s*"
subsecpat = r"##\s*([0-9]+)\.\s*(.*)\s*"
altcatpat = r"\(([0-9])\)([0-9]+)\.\s*(.*)\s*"

def build_xml(root, mdfname):
    with open(mdfname, encoding = 'utf8') as md:
        line = next(md)
        m = re.match(secpat, line)
        appendix = etree.SubElement(root, "appendix",
                                    title = m.group(1))
        point = appendix

        for line in md:
            line = line.strip()
            mss,mac = re.match(subsecpat, line), re.match(altcatpat,line)
            if mss:
                point = etree.SubElement(appendix,"alt_categorization",
                                         number = mss.group(1),
                                         title = mss.group(2))
            elif mac:
                subsec = mac.group(1)
                catnum = mac.group(2)
                catname = mac.group(3)
                cat = etree.SubElement(point,"category",
                                       name = mac.group(3),
                                       number = mac.group(2))
                line = next(md).strip()
                parser = etree.XMLParser()
                while not re.match("</ol>",line):
                    parser.feed(line)
                    line = next(md).strip()
                else:
                    parser.feed(line)
                OL = parser.close()
                for item in OL:
                    style = etree.SubElement(cat,"style")
                    style.text = item.text
            elif line:
                point = etree.SubElement(point,"paragraph")
                point.text = line
                point = point.getparent()

if __name__ == "__main__":
    from sys import argv
    MDfname = argv[1]
    if len(argv) > 2:
        XMLfname = argv[2]
    else:
        XMLfname = re.sub("\.md",".xml",\
                     re.sub("md/","xml/",MDfname))

    DocNode = etree.Element('doc')
    DocTree = etree.ElementTree(DocNode)

    build_xml(DocNode, MDfname)

    DocTree.write(XMLfname, pretty_print = True, encoding = 'utf8')
