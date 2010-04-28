#!/usr/bin/env python
#coding=utf-8
"""
© 2010 by Sven-S. Porst <ssp-web@earthlingsoft.net>

Skript zum Auslesen der Gedenktafeln berühmter Bewohner Göttingens von
	http://stadtarchiv.goettingen.de/texte/gedenktafelbuch.htm
und zum Umwandeln in eine KML Datei für Google Earth/Maps.

Verfügbar unter http://github.com/ssp/Gedenktafeln

Benötigt Mac OS X / PyObjC
"""



import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import re
from Foundation import *



"""
Es gibt verschiedene Probleme mit den vorhandenen Daten:
- Tippfehler
- Für Google nicht auffindbare Adressen
Diese Funktion, versucht, Adressen so gut wie möglich zu reparieren, um nur wenige Einträge zu verlieren.
"""
def fixaddress (string):
	string = string.replace(u"Geismarlandstr.", u"Geismar Landstraße") # Barbara OK
	string = string.replace(u"Geismarlandstraße", u"Geismar Landstraße") # Gauß, Klinkerfues, Weber, Schwarzschild, Schultz OK
	string = string.replace(u",\"Geophysikalisches Institut\"", "") # Bartels, Julius OK
	string = string.replace(u"Gotmarstraße 13", u"Gotmarstraße") # ? (# existiert nicht) OK
	string = string.replace(u"Gotmarstraße 8", u"Gotmarstraße") # Grotefeld (# existiert nicht) OK
	string = string.replace(u"Gotmarstraße 11", u"Gotmarstraße") # Gauß (# existiert nicht) OK
	string = string.replace(u"Gotmarstraße 1", u"Gotmarstraße") # Lichtenberg, zu Stolberg-Stolberg (# existiert nicht) OK
	string = string.replace(u"Gotmarstraße 3", u"Gotmarstraße") # Tychsen (# existiert nicht) OK
	string = string.replace(u"Kurze Straße 1", u"Kurze Straße") # Ehrenfeuchter (# existiert nicht) OK
	string = string.replace(u"Groner Straße 48", u"Groner Straße") #  Jahn (# existiert nicht) OK
	string = string.replace(u"staße", u"straße") # Franklin OK
	string = string.replace("Goethallee", "Goetheallee") # Gyarmathi OK
	string = string.replace("Walkenmühlenweg 30/32", "Walkemühlenweg 30") # Lotze 
	string = string.replace(u", heute Gebäude des Landkreises Göttingen, Reinhäuser Landstraße 4", "") # von Neumann OK
	string = string.replace(u"Stegmühlenweg", u"Stegemühlenweg") # Noether OK
	string = string.replace(u"Kurze Straße7", u"Kurze Straße 7") # Spittler OK
	string = string.replace("37/39", "37") # Taft OK
	string = string.replace(u"Böttiner Straße", u"Böttingerstraße") # Tollmien OK ?
	string = string.replace(u"Kurze Straße2", u"Kurze Straße 2") # Windthorst, Schücking OK
	string = string.replace(u"Sumpfebiel", u"Stumpfebiel") # Wolf OK
	
### funktionieren nicht
#	string = string.replace(u"Groner Straße 8", u"Groner Straße") #  Ewers (# existiert nicht)
# 	Elliehausen Kolbe
#	Hoher Weg 7 -> Göppert. In Bovenden?
#	Hoher Weg 7 -> Husserl

	return string




KML = NSXMLElement.elementWithName_("kml")
KML.addAttribute_(NSXMLNode.attributeWithName_stringValue_("xmlns", "http://earth.google.com/kml/2.1"))
KMLDocument = NSXMLElement.elementWithName_("Document")
KMLDocument.addChild_(NSXMLNode.elementWithName_stringValue_("name", u"Gedenktafeln an Göttinger Häusern"))
KML.addChild_(KMLDocument)


# ohne x
letters = "abcdefghijklmnopqrstuvwyz"


for letter in letters:
	filename = "Webseiten/" + letter + ".html"
	(HTMLString, error) = NSString.stringWithContentsOfFile_encoding_error_(filename, NSISOLatin1StringEncoding, None)
	if HTMLString == None:
		URL = NSURL.URLWithString_("http://stadtarchiv.goettingen.de/texte/gedenktafeln_" + letter + ".htm")
		HTMLData = NSData.dataWithContentsOfURL_(URL)
		HTMLString = NSString.alloc().initWithData_encoding_(HTMLData, NSISOLatin1StringEncoding)
		(result, error) = HTMLString.writeToFile_atomically_encoding_error_(filename, True, NSISOLatin1StringEncoding, None)

	(HTML, error) = NSXMLDocument.alloc().initWithXMLString_options_error_(HTMLString, NSXMLDocumentTidyHTML, None)

	XPath = "//td/ul/li"
	(nodes, error) = HTML.nodesForXPath_error_(XPath, None)

	for node in nodes:
		lines = node.stringValue().componentsSeparatedByString_("\n")
		if len(lines) > 2:
			name = lines[0]
			if len(name.split(",")) == 2:
				name = name.split(",")[1].strip() + " " + name.split(",")[0].strip()
			titel = lines[1]
			jahre = []
			
			for line in lines[2:]:
				if line[0] != "(":
					# Jahreszahlen
					jahre += [line]
				else:
					# Adresse
					adresse = fixaddress(line[1:-1])
					placemark = NSXMLElement.elementWithName_("Placemark")
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("name", name))
					volleadresse = adresse
					if adresse.find("Elliehausen") == -1:
						volleadresse =  adresse + u", Göttingen"
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("address", volleadresse))
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("description", titel + "\n" + ", ".join(jahre)))
					KMLDocument.addChild_(placemark)
					jahre = []

		else:
			print "No Data in record:"
			print lines
									
	
myXML = NSXMLDocument.alloc().initWithRootElement_(KML)
path = NSString.stringWithString_(u"~/Desktop/Gedenktafeln.kml").stringByExpandingTildeInPath()
data = myXML.XMLData()
data.writeToFile_atomically_(path, YES)