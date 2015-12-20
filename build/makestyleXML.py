"""Script to build XML version of a style category"""

from lxml import etree
import re

#This parser/builder assumes that within a style, any multi-paragraph
#descriptions are not separated by newlines in Markdown. That is, the
#parser reads style descriptors (aroma, flavor, etc.) until the next
#blank line.
#Style section heads in Markdown must in all cases be bolded, i.e.
#enclosed in **double asterisks**.

catpat = r"#\s*([0-9]+)\.\s*(.+)"
stylepat = r"##\s*(\**)([0-9]+)([A-Z])\.\s*(.+)\1"
stylesecpat = r"\*\*(.+?):\*\*\s*(.*)"

style_sections = ["Overall Impression", \
                  "Appearance", \
                  "Aroma", \
                  "Flavor", \
                  "Mouthfeel", \
                  "Comments", \
                  "History", \
                  "Characteristic Ingredients", \
                  "Style Comparison", \
                  "Entry Instructions", \
                  "Vital Statistics", \
                  "Commercial Examples", \
                  "Tags"]

vital_statistics = ["OG","FG","ABV","IBUs","SRM"]

def build_xml(root_node, mdfname):
    with open(mdfname, encoding = 'utf8') as md:
        line = next(md)
        m = re.match(catpat,line)
        if not m:
            raise Exception("This file does not appear to be a properly formatted BJCP category.")
        cat = etree.SubElement(root_node,"category",
                               number = m.group(1),
                               name = m.group(2))
        point = cat
        for line in md:
            if not line.strip():
                continue
            msty, mstysec = re.match(stylepat,line), re.match(stylesecpat,line)
            if msty:
                point = etree.SubElement(cat,'style',
                                         style_id = msty.group(2) + msty.group(3),
                                         style_name = msty.group(4))
            elif mstysec:
                if point.tag == "style":
                    secname = re.sub(' ','',mstysec.group(1)).lower()
                    if mstysec.group(1) == "Vital Statistics":
                        point = etree.SubElement(point,secname)
                        point.extend(parse_vital_statistics(md))
                        point = point.getparent()
                    elif mstysec.group(1) == "Commercial Examples":
                        point = etree.SubElement(point,secname)
                        for beer in mstysec.group(2).split(', '):
                            ex = etree.SubElement(point,"commercial_example")
                            ex.text = beer
                        point = point.getparent()
                    elif mstysec.group(1) == "Tags":
                        point = etree.SubElement(point,secname)
                        for tag in mstysec.group(2).split(', '):
                            t = etree.SubElement(point,"tag")
                            t.text = tag
                        point = point.getparent()
                    elif mstysec.group(1) in style_sections:
                        point = etree.SubElement(point,secname)
                        p = etree.SubElement(point,"paragraph")
                        p.text = mstysec.group(2)
                        line = next(md).strip()
                        while line:
                            p = etree.SubElement(point,"paragraph")
                            p.text = line
                            line = next(md).strip()
                        point = point.getparent()
                    else:
                        p = etree.SubElement(point,"paragraph")
                        p.text = mstysec.string
            else:
                p = etree.SubElement(point,"paragraph")
                p.text = line.strip()

def parse_vital_statistics(line_iterator):
    vspat = r"([a-zA-Z]+):\s*([0-9.]+)[\s%]*-\s*([0-9.]+)[\s%]*"
    line = next(line_iterator)
    try:
        while line.strip():
            m = re.match(vspat,line)
            yield etree.Element(m.group(1),low = m.group(2), high = m.group(3))
            line = next(line_iterator)
    except StopIteration:
        pass

if __name__ == "__main__":
    from sys import argv

    MDfname = argv[1]
    XMLfname = re.sub("\.md",".xml",\
                     re.sub("md/","xml/",MDfname))

    DocNode = etree.Element('doc')
    DocTree = etree.ElementTree(DocNode)

    build_xml(DocNode, MDfname)

    DocTree.write(XMLfname, pretty_print = True, encoding = 'utf8')
