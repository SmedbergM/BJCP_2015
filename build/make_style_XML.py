"""Script to build XML version of a style category"""

from lxml import etree
import re

#This parser/builder assumes that within a style, any multi-paragraph
#descriptions are not separated by newlines in Markdown. That is, the
#parser reads style descriptors (aroma, flavor, etc.) until the next
#blank line.
#Style section heads in Markdown must in all cases be bolded, i.e.
#enclosed in **double asterisks**.

cmntpat = r"\[//\]: # \((.+)\)"
catpat = r"#\s*([0-9]+)\.\s*(.+)"
stylepat = r"##\s*(\**)([0-9]+)([A-Z])\.\s*(.+)\1"
stylesecpat = r"\*\*(.+?):\*\*\s*(.*)"
substylepat = r"###\s*(.+?): (.+)"
commexpat = r"\{(.+?)\} ([^{}]*)"

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
            if re.match(cmntpat,line):
                continue
            elif line.strip():
                line = line.strip()
            else:
                continue
            msty, msubsty = re.match(stylepat,line), re.match(substylepat,line)
            if msty:
                point = etree.SubElement(cat,'style',
                                         style_id = msty.group(2) + msty.group(3),
                                         style_name = msty.group(4))
                point.extend(parse_sty(md))

                point = cat
            elif msubsty:
                point = etree.SubElement(cat,'style',
                                         style_name = msubsty.group(1),
                                         substyle_name = msubsty.group(2))
                point.extend(parse_sty(md))
                point = cat
            else:
                p = etree.SubElement(point,"paragraph")
                p.text = line.strip()

def parse_sty(line_iterator):
    for line in line_iterator:
        if re.match(cmntpat,line):
            continue
        elif line.strip():
            line = line.strip()
        else:
            continue
        mstysec, msubsty = re.match(stylesecpat,line), re.match(substylepat,line)
        if msubsty:
            point = etree.Element('substyle',
                                  style_name = msubsty.group(1),
                                  substyle_name = msubsty.group(2))
            point.extend(parse_sty(line_iterator))
            yield point
        elif mstysec:
            secname = re.sub(' ','',mstysec.group(1)).lower()
            if mstysec.group(1) == "Tags":
                point = etree.Element(secname)
                for tag in mstysec.group(2).split(', '):
                    t = etree.SubElement(point,"tag")
                    t.text = tag
                yield point
                break

                #NB: This routine uses the "tags" attribute as a sentinel
                #for the end of the style. For styles with substyles (such
                #as 7C Kellerbier) we must insert an empty "tags" line
                #at the end of the style. This is hacky, but I don't see a
                #better way to read the end of a style without either
                #(a) reading the header line of the next style, and hence
                #needing to pass it up the stack somehow;
                #(b) reading the whole .md file in at once using readlines()
                #(c) hand-adding a comment at the end of each style to use as
                #a non-printing sentinel.
                #If it turns out that every substyle occurs at the end of its
                #respective category, then we can just delete this hack.

            elif mstysec.group(1) == "Vital Statistics":
                point = etree.Element(secname)
                if mstysec.group(2):
                    p = etree.SubElement(point,"paragraph")
                    p.text = mstysec.group(2)
                point.extend(parse_vital_statistics(line_iterator))
                yield point
            elif mstysec.group(1) == "Commercial Examples":
                point = etree.Element(secname)
                if re.search(commexpat,line):
                    for group,beers in re.findall(commexpat,line):
                        for beer in beers.strip().split(', '):
                            ex = etree.SubElement(point,"commercial_example",group = group)
                            ex.text = beer
                else:
                    for beer in mstysec.group(2).split(', '):
                        ex = etree.SubElement(point,"commercial_example")
                        ex.text = beer
                yield point
            elif mstysec.group(1) in style_sections:
                point = etree.Element(secname)
                p = etree.SubElement(point,"paragraph")
                p.text = mstysec.group(2)
                line = next(line_iterator).strip()
                while line:
                    p = etree.SubElement(point,"paragraph")
                    p.text = line
                    line = next(line_iterator).strip()
                yield point
            else:
                p = etree.Element("paragraph")
                p.text = line.strip()
                yield p
        else:
            p = etree.Element("paragraph")
            p.text = line.strip()
            yield p

def parse_vital_statistics(line_iterator):
    vspat = r"([a-zA-Z]+):\s*([0-9.]+)[\s%]*-\s*([0-9.]+)[\s%]*(.*)"
    vsvarpat = r"([a-zA-Z]+):\s*(.*)"
    line = next(line_iterator).strip()
    try:
        while line:
            mvs,mvar = re.match(vspat,line), re.match(vsvarpat,line)
            if mvs:
                vs = etree.Element(mvs.group(1), low = mvs.group(2), high = mvs.group(3))
                if mvs.group(4):
                    vs.text = mvs.group(4)
            elif mvar:
                vs = etree.Element(mvar.group(1))
                vs.text = mvar.group(2)
            else:
                vs = etree.Element("paragraph")
                vs.text = line
            yield vs
            line = next(line_iterator).strip()
    except StopIteration:
        pass

if __name__ == "__main__":
    from sys import argv

    MDfname = argv[1]
    if len(argv) > 2:
        XMLfname = argv[2]
    else:
        XMLfname = re.sub("\.md",".xml",
                          re.sub("md/","xml/",MDfname))

    DocNode = etree.Element('doc')
    DocTree = etree.ElementTree(DocNode)

    build_xml(DocNode, MDfname)

    DocTree.write(XMLfname, pretty_print = True, encoding = 'utf8')
