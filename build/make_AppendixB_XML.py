import re
from lxml import etree

titlepat = r"#\s*(.*)\s*"
secpat = r"##\s*(.+)\s*"
stypat = r"##\s*(X[0-9])\.\s*(.+)\s*"
stysecpat = r"\*\*(.+?):\*\*\s*(.*)\s*"
vspat = r"\*\*(Vital Statistics):\*\*\s*"
evpat = r"\*\*(Estadísticas vitales):\*\*"
statpat = r"([a-zA-Z.]+):\s*([0-9.,]+)[\s%º]*-\s*([0-9,.]+)[\s%º]*"

def build_xml(root,mdfname):
    with open(mdfname, encoding = 'utf8') as md:
        line = next(md).strip()
        m = re.match(titlepat,line)
        appendix = etree.SubElement(root,"appendix",
                                    title = m.group(1))

        point = appendix

        for line in md:
            line = line.strip()
            msty = re.match(stypat,line)
            msec = re.match(secpat,line)
            mvs = re.match(vspat,line)
            mev = re.match(evpat,line)
            mstysec = re.match(stysecpat,line)
            if msty:
                point = etree.SubElement(loc,"style",
                                         style_id = msty.group(1),
                                         style_name = msty.group(2))
            elif msec:
                loc = etree.SubElement(appendix,"locality",
                                         location = msec.group(1))
                point = loc
            elif mvs:
                point = etree.SubElement(point,"vitalstatistics")
                try:
                    line = next(md).strip()
                    while line:
                        m = re.match(statpat,line)
                        stat = etree.SubElement(point,
                                                re.sub("\.","",m.group(1)),
                                                low = m.group(2),
                                                high = m.group(3))
                        line = next(md).strip()
                    else:
                        point = point.getparent()
                except StopIteration:
                    point = point.getparent()
                    break
            elif mev:
                point = etree.SubElement(point,"estadísticasvitales")
                try:
                    line = next(md).strip()
                    while line:
                        m = re.match(statpat,line)
                        stat = etree.SubElement(point,
                                                re.sub("\.","",m.group(1)),
                                                low = m.group(2),
                                                high = m.group(3))
                        line = next(md).strip()
                    else:
                        point = point.getparent()
                except StopIteration:
                    point = point.getparent()
                    break
                
            elif mstysec:
                point = etree.SubElement(point,"style_section",
                                         section_name = mstysec.group(1))
                par = etree.SubElement(point,"paragraph")
                if "Commercial Examples" in mstysec.group(1):
                    for beer in mstysec.group(2).split(', '):
                        ex = etree.SubElement(point,"commercial_example")
                        ex.text = beer
                elif "Ejemplos comerciales" in mstysec.group(1):
                    for beer in mstysec.group(2).split(', '):
                        ex = etree.SubElement(point,"ejemplo_comercial")
                        ex.text = beer
                else:
                    par.text = mstysec.group(2)
                    try:
                        line = next(md).strip()
                        while line:
                            par = etree.SubElement(point,"paragraph")
                            par.text = line
                            line = next(md).strip()
                    except StopIteration:
                        break
                point = point.getparent()
            elif line:
                par = etree.SubElement(point,"paragraph")
                par.text = line
                

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
