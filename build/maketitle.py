"""Script to build the title page XML for the 2015 BJCP Guidelines."""

from lxml import etree
import re

## The formatting on titlepage.md does not reflect the hierarchical
## structuring of information found in the remainder of the project.
## Hence it requires its own XML builder.

secpat = r"(#+)\s*(.+)"
cmntpat = r"\[//\]: # \((.+)\)"

contrib_types = ['editor','coeditor','pastguidelineanalysis',\
                 'newstylecontributions','reviewandcommentary',\
                 'finalreview']

DocNode = etree.Element('doc')
DocTree = etree.ElementTree(DocNode)

with open('../md/titlepage.md','r', encoding = 'utf8') as md:
    for line in (line.strip() for line in md if line.strip()):
        mc,ms = re.match(cmntpat,line),re.match(secpat,line)
        if mc:
            point = etree.SubElement(DocNode,mc.group(1))
        elif ms:
            hdr = etree.SubElement(point,"h{0:d}".format(len(ms.group(1))))
            hdr.text = ms.group(2)
        elif point.tag in contrib_types:
            for name in line.split(', '):
                contrib = etree.SubElement(point,"contributor")
                contrib.text = name
        else:
            par = etree.SubElement(point,"paragraph")
            par.text = line

DocTree.write('../xml/titlepage.xml', pretty_print = True, encoding = 'utf8')
