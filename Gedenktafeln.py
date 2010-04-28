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

import httplib
import urllib
def personeninfo (name):
	print
	print "personeninfo called for === " + name + " ==="

	filename = "Personen/" + name + ".html"
	(personXHTMLString, error) = NSString.stringWithContentsOfFile_encoding_error_(filename, NSUTF8StringEncoding, None)
	personXHTML = None
	if personXHTMLString != None:
		(personXHTML, error) = NSXMLDocument.alloc().initWithXMLString_options_error_(personXHTMLString, NSXMLDocumentTidyXML, None)
		if personXHTML != None:
			print "	Cached file parsed successfully"
	
	if personXHTML == None:
		print "	Searching for person"
		url = NSURL.URLWithString_("http://toolserver.org/~apper/pd/index.php")
		
		connection = httplib.HTTPConnection("toolserver.org")
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/xml,application/xhtml+xml,text/html"}
		params = urllib.urlencode({"name": name})
		connection.request("POST", "/~apper/pd/index.php", params, headers)
		response = connection.getresponse()
		ergebnis = response.read()
		connection.close()

		(XML, error) = NSXMLDocument.alloc().initWithXMLString_options_error_(ergebnis, NSXMLDocumentTidyXML, None)
		if XML == None:
			print "	Failed to read server answer"
		XPath = """//div[@class="moreinfo"]/a/@href"""
		(nodes, error) = XML.nodesForXPath_error_(XPath, None)
		
		if nodes.count() == 1:
			moreInfoURL = NSURL.URLWithString_("http://toolserver.org" + nodes[0].stringValue())
			if moreInfoURL != None:
				print "	more Information at: " + str(moreInfoURL)
				(personXHTML, error) = NSXMLDocument.alloc().initWithContentsOfURL_options_error_(moreInfoURL, NSXMLDocumentTidyXML, None)
				if personXHTML != None:
					print "		successfully read additional information"
					personXHTML.XMLData().writeToFile_atomically_(filename, True)
				else:
					print "		could not read additional information"
			else:
				print " 	could not figure out address of additional information"
		else:
			print "	" + str(nodes.count()) + " matches: don't know which one to pick"

	imageURL = None
	imagePageURL = None
	personPageURL = None

	if personXHTML != None:
	
		XPath = """//div[@id="header_persons"]/div/img/@src"""
		(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
		if nodes.count() == 1:
			imageURL = nodes[0].stringValue()
			if imageURL.find("placeholder.jpg"):
				imageURL = None
		print "	image URL: " + str(imageURL)

		XPath = """//div[@id="img_info"]/a/@href"""
		(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
		if nodes.count() == 1:
			imagePageURL = nodes[0].stringValue()

		print "	imagePageURL: " + str(imagePageURL)

		XPath = """//div[@id="main"]/div[@class="person_name"]/a/@href"""
		(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
		if nodes.count() == 1:
			personPageURL = nodes[0].stringValue()
		print "	Wikipedia URL: " + str(personPageURL)
		
	return imageURL




KML = NSXMLElement.elementWithName_("kml")
KML.addAttribute_(NSXMLNode.attributeWithName_stringValue_("xmlns", "http://earth.google.com/kml/2.1"))
KMLDocument = NSXMLElement.elementWithName_("Document")
KMLDocument.addChild_(NSXMLNode.elementWithName_stringValue_("name", u"Gedenktafeln an Göttinger Häusern"))
KML.addChild_(KMLDocument)


# ohne x
letters = "abcdefghijklmnopqrstuvwyz"
#letters = "y"

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
			info = personeninfo(name)
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