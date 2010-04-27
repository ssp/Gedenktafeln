#!/usr/bin/env python
#coding=utf-8
"""
Skript zum Auslesen der Gedenktafeln berühmter Bewohner Göttingens von
	http://stadtarchiv.goettingen.de/texte/gedenktafelbuch.htm
und zum Umwandeln in eine KML Datei für Google Earth/Maps.

Benötigt Mac OS X / PyObjC
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Foundation import *

KML = NSXMLElement.elementWithName_("kml")
KML.addAttribute_(NSXMLNode.attributeWithName_stringValue_("xmlns", "http://earth.google.com/kml/2.1"))
KMLDocument = NSXMLElement.elementWithName_("Document")
KMLDocument.addChild_(NSXMLNode.elementWithName_stringValue_("name", u"Gedenktafeln an Göttinger Häusern"))
KML.addChild_(KMLDocument)


# ohne x
letters = "abcdefghijklmnopqrstuvwyz"
#letters = "r"

for letter in letters:
	URL = NSURL.URLWithString_("http://stadtarchiv.goettingen.de/texte/gedenktafeln_" + letter + ".htm")
	HTMLData = NSData.dataWithContentsOfURL_(URL)
	HTMLString = NSString.alloc().initWithData_encoding_(HTMLData, NSISOLatin1StringEncoding)
	(HTML, error) = NSXMLDocument.alloc().initWithXMLString_options_error_(HTMLString, NSXMLDocumentTidyHTML, None)
	HTMLString.release()

	XPath = "//td/ul/li"
	(nodes, error) = HTML.nodesForXPath_error_(XPath, None)

	for node in nodes:
		lines = node.stringValue().componentsSeparatedByString_("\n")
		name = lines[0]
		titel = ""
		i = 1
		if len(lines) % 2 == 0:
			titel = lines[1]
			i = 2
		while i + 1 < len(lines):
			jahre = lines.objectAtIndex_(i)
			adresse = lines[i+1][1:-1]
			
			placemark = NSXMLElement.elementWithName_("Placemark")
			placemark.addChild_(NSXMLNode.elementWithName_stringValue_("name", name))
			placemark.addChild_(NSXMLNode.elementWithName_stringValue_("address", adresse + u"\nGöttingen"))
			placemark.addChild_(NSXMLNode.elementWithName_stringValue_("description", titel + "\n" + jahre))

			KMLDocument.addChild_(placemark)
			
			i = i + 2
			
	
myXML = NSXMLDocument.alloc().initWithRootElement_(KML)
path = NSString.stringWithString_(u"~/Desktop/Gedenktafeln.kml").stringByExpandingTildeInPath()
data = myXML.XMLData()
data.writeToFile_atomically_(path, YES)