#!/usr/bin/env python
#coding=utf-8
"""
© 2010 by Sven-S. Porst <ssp-web@earthlingsoft.net>

Skript zum Auslesen der Gedenktafeln berühmter Bewohner Göttingens von
	http://stadtarchiv.goettingen.de/texte/gedenktafelbuch.htm
und zum Umwandeln in eine KML Datei "Gedenktafeln.html" für Google Earth/Maps, die auf dem Schreibtisch gesichert wird.

Verfügbar unter http://github.com/ssp/Gedenktafeln

Das Ergebnis läßt sich unter http://earthlingsoft.net/ssp/Gedenktafeln betrachten.

Benötigt Mac OS X / PyObjC
"""

"""
Das Skript versucht heruntergeladene Informationen lokal zu cachen, um die Anzahl der benötigten Downloads zu reduzieren.

Die folgenden Ordner sollten existieren:
- Webseiten: für die Informationen vom Stadtarchiv Göttingen
- Personen: für die Informationen von der Wikipedia Suche
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


"""
Viel Handarbeit, um die richtigen Wikipedia-Einträgen Namen zuzuordnen.
"""
personURLHints = {
"Adolf Friedrich": "Adolph_Friedrich,_Herzog_von_Cambridge",
"Altenstein, Karl Sigmund Franz Freiherr vom Stein zum": "Karl_vom_Stein_zum_Altenstein",
"Arnim, Achim von": "Achim_von_Arnim",
"August Friedrich": "Augustus_Frederick,_Duke_of_Sussex",
"Bancroft, George": "George_Bancroft_(Politiker)",
"Barbara": u"Barbara_(Sängerin)",
"Barth, Karl": "Karl_Barth",
"Bauer, Walter": "Walter_Bauer_(Theologe)",
"Baum, Wilhelm": "Wilhelm_Baum_(Chirurg)",
"Becker, Richard": "Richard_Becker_(Physiker)",
"Beckmann, Johann": "Johann_Beckmann",
"Bismarck, Otto von": "Otto_von_Bismarck",
"Bizyenos, Georgios": "Georgios_Vizyinos",
"Brandl, Alois": "Alois_Brandl_(Literaturwissenschaftler)",
"Brentano, Clemens Wenzel Maria": "Clemens_Brentano",
"Brugsch, Heinrich F. K.": "Heinrich_Brugsch",
"Bunsen, Christian Karl Josias Freiherr von": "Christian_Karl_Josias_von_Bunsen",
u"Bürger, Gottfried August": u"Gottfried_August_Bürger",
"Clark, William S.": "William_Smith_Clark",
"Clebsch, Rudolf Friedrich Alfred": "Alfred_Clebsch",
"Coleridge, Samuel Taylor": "Samuel_Taylor_Coleridge",
"Constant, Benjamin": "Benjamin_Constant",
u"Csoma, Alexander von Körös": "Sándor_Csoma",
"Curtius, Ernst": "Ernst_Curtius", 
"Dehio, Georg Gottfried Julius": "Georg_Dehio",
"Diez, Friedrich": "Friedrich_Christian_Diez",
"Ehrenfeuchter, Friedrich August Eduard": "Friedrich_Ehrenfeuchter",
"Eichhorn, Joh. Gottfried": "Johann_Gottfried_Eichhorn",
"Ernst August": "Ernst_August_I._(Hannover)",
"Erxleben, Johann Christian Polycarp": "Johann_Christian_Erxleben",
"Esmarch, Johannes Friedrich August von": "Friedrich_von_Esmarch",
"Arthur J. Evans": "Arthur_Evans",
"Edward Everett": "Edward_Everett",
"Fliedner, Theodor": "Theodor_Fliedner",
"Forster, Georg": "Georg_Forster",
"Franklin, Benjamin": "Benjamin_Franklin",
"Frege, Gottlob": "Gottlob_Frege",
u"Fröbel, Friedrich Wilhelm August": u"Friedrich_Fröbel",
}




"""
Tippfehler in Namen korrigieren
"""
namenskorrekturen = {
"Benecke, George Friedrich": "Benecke, Georg Friedrich",
"Boie, Henrich Christian": "Boie, Heinrich Christian"
}

def namenskorrektur (name):
	if namenskorrekturen.has_key(name):
		return namenskorrekturen[name]
	else:
		return name.strip()


"""
Tippfehler in Titeln korrigieren
"""
titelkorrekturen = {

}

def titelkorrektur (titel):
	if titelkorrekturen.has_key(titel):
		return titelkorrekturen[titel]
	else:
		return titel





import httplib
import urllib
"""
Sammelt Informationen über die Person über eine Namenssuche in den den Wikipedia Einträgen.

Leider ist die Suche nicht besonders gut und findet viele offensichtliche Treffer nicht, so daß "PersonURLHints" genutzt wird, um dem Skript zu helfen. (Um alles unangenehmer zu machen, nutzen die Suchergebnisse manchmal andere Dateinamen in den Pfaden als die richtige Wikipedia, yay!)
"""
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
		personURLString = None
		nodes = NSArray.array()

		if personURLHints.has_key(name):
			personURLString = "http://toolserver.org/~apper/pd/person/" + personURLHints[name]
			print "	using hint for correct person"
		else:
			url = NSURL.URLWithString_("http://toolserver.org/~apper/pd/index.php")
		
			connection = httplib.HTTPConnection("toolserver.org")
			headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/xml,application/xhtml+xml,text/html"}
			params = urllib.urlencode({"name": name})
			connection.request("POST", "/~apper/pd/index.php", params, headers)
			response = connection.getresponse()
			ergebnis = response.read()
			connection.close()

			# ergebnis String ist UTF-8 gelesen als Latin-1, also reparieren
			stringData = NSString.stringWithString_(ergebnis).dataUsingEncoding_(NSISOLatin1StringEncoding)
			ergebnis = NSString.alloc().initWithData_encoding_(stringData, NSUTF8StringEncoding)
			(XML, error) = NSXMLDocument.alloc().initWithXMLString_options_error_(ergebnis, NSXMLDocumentTidyXML, None)

			if XML == None:
				print "	Failed to read server answer"
			XPath = """//div[@class="moreinfo"]/a/@href"""
			(nodes, error) = XML.nodesForXPath_error_(XPath, None)
		
		if nodes.count() == 1:
			personURLString = NSString.stringWithString_("http://toolserver.org").stringByAppendingString_(nodes[0].stringValue())
		elif nodes.count() > 1:
			print "	" + str(nodes.count()) + " matches: don't know which one to pick"

		if personURLString != None:
			personURL = NSURL.URLWithString_(personURLString)
			if personURL != None:
				print "	more Information at: " + str(personURLString)
				(personXHTML, error) = NSXMLDocument.alloc().initWithContentsOfURL_options_error_(personURL, 	NSXMLDocumentTidyXML, None)
				if personXHTML != None:
					print "		successfully read additional information"
					personXHTML.XMLData().writeToFile_atomically_(filename, True)
				else:
					print "		could not read additional information"
			else:
				print "		could not build URL with additional information"
		else:
			print " 	could not figure out address of additional information"

	imageURL = None
	imagePageURL = None
	wikipediaURL = None

	if personXHTML != None:
		XPath = """//div[@id="header_persons"]/div/img/@src"""
		(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
		if nodes.count() == 1:
			imageURL = nodes[0].stringValue()
			if imageURL.find("placeholder.jpg") != -1:
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
			wikipediaURL = nodes[0].stringValue()
		print "	Wikipedia URL: " + str(wikipediaURL)
		
	return {"imageURL": imageURL, "imagePageURL": imagePageURL, "wikipediaURL": wikipediaURL}




"""
HTML für die "Sprechblase" auf der Karte erzeugen.
Nutzt die Datei Bubble.html als Vorlage.
"""
def makeDescription(name, titel, jahre, adresse, info):
	(htmlString, error) = NSString.stringWithContentsOfFile_encoding_error_("Bubble.html", NSUTF8StringEncoding, None)
	
	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("NAME", name)
	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("TITEL", titel)
	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("JAHRE", "und ".join(jahre))

	imageTag = ""
	if info["imageURL"] != None and info["imagePageURL"] != None:
		imageTag = "<a class='portraitlink' href='" +  info["imagePageURL"] + "' title='Wikipedia Bildseite'><img class='portrait' src='" + info["imageURL"] + "' alt='" + name + "'/></a>"
	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("IMAGETAG", imageTag)

	wikipediaTag = ""
	if info["wikipediaURL"] != None:
		wikipediaTag = "<p><a href='" + info["wikipediaURL"] + "'>Wikipedia Seite »</a></p>"
#		wikipediaTag = "<iframe src='" + info["wikipediaURL"] + "'>"

	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("WIKIPEDIATAG", wikipediaTag)
	
	return htmlString






"""
Skriptbeginn
"""


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
			name = namenskorrektur(lines[0])
			titel = titelkorrektur(lines[1])
			info = personeninfo(name)
			reversedname = name
			if len(name.split(",")) == 2:
				reversedname = name.split(",")[1].strip() + " " + name.split(",")[0].strip()
			jahre = []
			
			for line in lines[2:]:
				if line[0] != "(":
					# Jahreszahlen
					jahre += [line]
				else:
					# Adresse
					adresse = fixaddress(line[1:-1])
					placemark = NSXMLElement.elementWithName_("Placemark")
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("name", reversedname))
					volleadresse = adresse
					if adresse.find("Elliehausen") == -1:
						volleadresse =  adresse + u", Göttingen"
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("address", volleadresse))
					description = makeDescription(name, titel, jahre, adresse, info)
					placemark.addChild_(NSXMLNode.elementWithName_stringValue_("description", description))
					KMLDocument.addChild_(placemark)
					jahre = []

		else:
			print "No Data in record:"
			print lines
									
	
myXML = NSXMLDocument.alloc().initWithRootElement_(KML)
path = NSString.stringWithString_(u"~/Desktop/Gedenktafeln.kml").stringByExpandingTildeInPath()
data = myXML.XMLData()
data.writeToFile_atomically_(path, YES)