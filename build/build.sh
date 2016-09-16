#!/bin/bash

## bash script for generating the xml files

cd `dirname $0` && cd ..

PYTHON="env python3"
ls md | sed -e '/^[0-9]/p' -e 'd' | while read MD_FILE; do 
	XML_FILE=$(echo $MD_FILE | sed -e 's:\.md:\.xml:g')
	$PYTHON build/make_style_XML.py md/$MD_FILE xml/$XML_FILE || exit 1
done

$PYTHON build/make_title.py md/Title_Page.md xml/Title_Page.xml
$PYTHON build/make_text_XML.py md/Introduction_to_Beer_Styles.md xml/Introduction_to_Beer_Styles.xml 
$PYTHON build/make_text_XML.py md/Introduction_to_Specialty_Type_Beer.md  xml/Introduction_to_Specialty_Type_Beer.xml 
$PYTHON build/make_text_XML.py md/Introduction_to_the_2015_Guidelines.md xml/Introduction_to_the_2015_Guidelines.xml 
$PYTHON build/make_AppendixA_XML.py md/AppendixA.md  xml/AppendixA.xml 
$PYTHON build/make_AppendixB_XML.py md/AppendixB.md  xml/AppendixB.xml 






