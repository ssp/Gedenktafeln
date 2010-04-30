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


"""
Eintrag für Hölty falsch?
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
"Adolf Friedrich": "Adolphus_Frederick,_1._Duke_of_Cambridge",
"Altenstein, Karl Sigmund Franz Freiherr vom Stein zum": "Karl_vom_Stein_zum_Altenstein",
"Arnim, Achim von": "Achim_von_Arnim",
"August Friedrich": "Augustus_Frederick,_Duke_of_Sussex",
"Auwers, Arthur Julius Georg Friedrich von": "http://de.wikipedia.org/wiki/Arthur_Auwers",
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
u"Csoma, Alexander von Körös": u"Sándor_Csoma",
"Curtius, Ernst": "Ernst_Curtius", 
"Dehio, Georg Gottfried Julius": "Georg_Dehio",
"Diez, Friedrich": "Friedrich_Christian_Diez",
"Ehrenfeuchter, Friedrich August Eduard": "Friedrich_Ehrenfeuchter",
"Eichhorn, Joh. Gottfried": "Johann_Gottfried_Eichhorn",
"Ernst August": u"Ernst_August_I._(Hannover)",
"Erxleben, Johann Christian Polycarp": "Johann_Christian_Erxleben",
"Esmarch, Johannes Friedrich August von": "Friedrich_von_Esmarch",
"Evans, Arthur J.": "http://de.wikipedia.org/wiki/Arthur_Evans",
"Everett, Edward": "Edward_Everett",
"Fliedner, Theodor": "Theodor_Fliedner",
"Forster, Georg": "Georg_Forster",
"Franklin, Benjamin": "Benjamin_Franklin",
"Frege, Gottlob": "Gottlob_Frege",
u"Fröbel, Friedrich Wilhelm August": u"http://de.wikipedia.org/wiki/Friedrich_Wilhelm_August_Fröbel", # nicht im Namensserver?
"Georg V.": "Georg_V._(Hannover)", 
"Gerlach, Leopold von": "Ludwig_Friedrich_Leopold_von_Gerlach",
"Goldschmidt, Victor Moritz": "http://de.wikipedia.org/wiki/Viktor_Moritz_Goldschmidt",
"Grimm, Jacob und Wilhelm": u"http://de.wikipedia.org/wiki/Brüder_Grimm", # speziell behandeln? / einzelne nicht im Namensserver
"Gruner, Justus von": "Justus_von_Gruner",
"Hagen, Oskar": "Oskar_Hagen",
"Hahn, Otto": "Otto_Hahn",
"Hanssen, Georg": "Georg_Hanssen",
"Heine, Heinrich": "http://de.wikipedia.org/wiki/Heinrich_Heine",
"Henle, Friedrich Gustav Jacob": "Jakob_Henle",
"Henneberg, Wilhelm": "Wilhelm_Henneberg",
"Hermann, Carl Friedrich": "Karl_Friedrich_Hermann",
"Heyne, Moritz": "http://de.wikipedia.org/wiki/Moritz_Heyne",
"Honda, Kotaro": u"Kōtarō_Honda",
"Hugo, Gustav": u"Gustav_von_Hugo",
"Joachim, Joseph": u"Joseph_Joachim",
"Kaestner, Abraham Gotthelf": u"Abraham_Gotthelf_Kästner",
u"König, Franz": u"http://de.wikipedia.org/wiki/Franz_König_(Chirurg)",
"Lachmann, Karl Konrad Friedrich Wilhelm": "http://de.wikipedia.org/wiki/Karl_Lachmann",
"Langenbeck, Bernhard Conrad Rudolf von": "http://de.wikipedia.org/wiki/Bernhard_von_Langenbeck",
"Ludwig I.": "http://de.wikipedia.org/wiki/Ludwig_I._(Bayern)",
u"Ludwig IV. Großherzog von Hessen": u"http://de.wikipedia.org/wiki/Ludwig_IV._(Hessen-Darmstadt)",
u"Maximilian II.": u"http://de.wikipedia.org/wiki/Maximilian_II._Joseph_(Bayern)",
"Mayer, Tobias": "http://de.wikipedia.org/wiki/Tobias_Mayer",
"Miquel, Johann Franz von": "http://de.wikipedia.org/wiki/Johannes_von_Miquel",
"Mitscherlich, Eilhard": "http://de.wikipedia.org/wiki/Eilhard_Mitscherlich",
u"Müller, Johannes von": u"http://de.wikipedia.org/wiki/Johannes_von_Müller",
"Olbers, Wilhelm": "http://de.wikipedia.org/wiki/Heinrich_Wilhelm_Olbers",
"Planck, Gottlieb": "http://de.wikipedia.org/wiki/Gottlieb_Planck",
"Plessner, Helmuth": "http://de.wikipedia.org/wiki/Helmuth_Plessner",
"Pohl, Robert W.": "http://de.wikipedia.org/wiki/Robert_Wichard_Pohl",
"Ritschl, Albrecht Benjamin": "http://de.wikipedia.org/wiki/Albrecht_Ritschl_(Theologe)",
"Ritter, August Heinrich": "http://de.wikipedia.org/wiki/Heinrich_Ritter",
"Ritter, Karl": "http://de.wikipedia.org/wiki/Carl_Ritter",
"Roth, Heinrich": u"http://de.wikipedia.org/wiki/Heinrich_Roth_(Pädagoge)",
"Savigny, Friedrich Carl von": "http://de.wikipedia.org/wiki/Friedrich_Carl_von_Savigny",
u"Schlözer, August Ludwig von": u"http://de.wikipedia.org/wiki/August_Ludwig_von_Schlözer",
u"Schroeter, Joh. Hyronimus": u"http://de.wikipedia.org/wiki/Johann_Hieronymus_Schröter",
u"Schücking, Christoph Bernhard Levin": u"http://de.wikipedia.org/wiki/Levin_Schücking",
u"Schulenburg, Fritz-Dietlof Graf v.d.": u"http://de.wikipedia.org/wiki/Fritz-Dietlof_Graf_von_der_Schulenburg",
"Schultz, Ernst Andreas Heinrich Hermann": "http://de.wikipedia.org/wiki/Hermann_Schultz",
"Siebold, Eduard Karl Kaspar Jakob von": "http://de.wikipedia.org/wiki/Eduard_Caspar_Jacob_von_Siebold",
"Smend, Rudolf": "http://de.wikipedia.org/wiki/Rudolf_Smend",
"Soetbeer, Georg Adolf": "http://de.wikipedia.org/wiki/Soetbeer",
"Spitta, Karl Johann Philipp": "http://de.wikipedia.org/wiki/Philipp_Spitta",
"Spittler, Ludwig Timotheus Freiherr von": "http://de.wikipedia.org/wiki/Ludwig_Timotheus_Spittler",
"Stolberg-Stolberg, Christian Graf zu": "http://de.wikipedia.org/wiki/Christian_zu_Stolberg-Stolberg",
"Stolberg- Stolberg, Friedrich Leopold Graf zu": "http://de.wikipedia.org/wiki/Friedrich_Leopold_zu_Stolberg-Stolberg",
"Tammann, Gustav": "http://de.wikipedia.org/wiki/Gustav_Tammann",
"Thorbecke, Johan Rudolf": "http://de.wikipedia.org/wiki/Johan_Rudolf_Thorbecke",
"Treitschke, Heinrich von": "http://de.wikipedia.org/wiki/Heinrich_von_Treitschke",
"Voss, Johann Heinrich": u"http://de.wikipedia.org/wiki/Johann_Heinrich_Voß",
"Wagner, Hermann": "http://de.wikipedia.org/wiki/Hermann_Wagner_(Geograph)",
"Wagner, Rudolf": "http://de.wikipedia.org/wiki/Rudolf_Wagner_(Mediziner)",
"Waitz, Georg": "http://de.wikipedia.org/wiki/Georg_Waitz",
"Weber, Werner": "http://de.wikipedia.org/wiki/Werner_Weber_(Jurist)",
"Weber, Wilhelm": "http://de.wikipedia.org/wiki/Wilhelm_Eduard_Weber",
"Wied, Maximilian, Prinz zu": "http://de.wikipedia.org/wiki/Maximilian_zu_Wied-Neuwied",
"Wilhelm II.": u"http://de.wikipedia.org/wiki/Wilhelm_II._(Württemberg)",
"Wilhelm August Ludwig": "http://de.wikipedia.org/wiki/Wilhelm_(Braunschweig)",
"Young, Thomas": "http://de.wikipedia.org/wiki/Thomas_Young_(Physiker)",
"Zimmerli, Walther": "http://de.wikipedia.org/wiki/Walther_Zimmerli",
}




"""
Tippfehler in Namen korrigieren und Namensschreibweisen anpassen.
"""
namenskorrekturen = {
"Benecke, George Friedrich": "Benecke, Georg Friedrich",
"Boie, Henrich Christian": "Boie, Heinrich Christian",
"Goeschen, Johann Friedrich Ludwig": u"Göschen, Johann Friedrich Ludwig",
"Gauss, Johann Carl Friedrich": u"Gauß, Johann Carl Friedrich",
"Lietzmann, Walter": "Lietzmann, Walther",
"Listing, Johann Benedikt": "Listing, Johann Benedict",
"Lotze, Rudolph Hermann": "Lotze, Rudolf Hermann",
"Nernst, Walter": "Nernst, Walther",
"Richter, August Gottlob": "Richter, August Gottlieb",
"Siegel, Carl L.": "Siegel, Carl Ludwig",

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
"Geschitsschreiber": "Geschichtsschreiber",
"Methematiker und Astronom": "Mathematiker und Astronom",
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
	
	personURLString = None
	if personURLHints.has_key(name):
		personURLString = personURLHints[name]
		if personURLString.find("wikipedia") == -1:
			personURLString = "http://toolserver.org/~apper/pd/person/" + personURLString
		print "	using hint for correct person"

	if personXHTML == None:
		print "	Searching for person"
		nodes = NSArray.array()
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
			print "	" + str(nodes.count()) + " matches: don't know which one to pick ****************"

		if personURLString != None:
			personURLString = NSString.stringWithString_(personURLString).stringByAddingPercentEscapesUsingEncoding_(NSUTF8StringEncoding)
			personURL = NSURL.URLWithString_(personURLString)
			if personURL != None:
				print "	more Information at: " + str(personURLString)
				(personXHTML, error) = NSXMLDocument.alloc().initWithContentsOfURL_options_error_(personURL, 	NSXMLDocumentTidyXML, None)
				if personXHTML != None:
					print "		successfully read additional information"
					personXHTML.XMLData().writeToFile_atomically_(filename, True)
				else:
					print "		could not read additional information ******************"
			else:
				print "		could not build URL with additional information ****************"
		else:
			print " 	could not figure out address of additional information ****************"

	imageURL = None
	imagePageURL = None
	wikipediaURL = None

	if personXHTML != None:
		XPath = """//div[@id="globalWrapper"]"""
		(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
		
		if nodes.count() != 0:
			# info von Wikipedia Seite
			XPath = """//div[@class="thumbinner"]/a[@class="image"]/img[@class="thumbimage"]/@src"""
			(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
			if nodes.count() > 0:
				imageURL = nodes[0].stringValue()
				if imageURL.find ("wikipedia") != -1:
					imageURL = "http://de.wikipedia.org" + imageURL
	
			XPath = """//div[@class="thumbinner"]/a[@class="image"]/@href"""
			(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
			if nodes.count() > 0:
				imagePageURL = nodes[0].stringValue()
				if imagePageURL.find ("wikipedia") != -1:
					imagePageURL = "http://de.wikipedia.org" + imagePageURL
			
			wikipediaURL = personURLString
			print "	extracted information from Wikipedia page"
			
		else:
			# info aus der personensuche
			XPath = """//div[@id="header_persons"]/div/img/@src"""
			(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
			if nodes.count() == 1:
				imageURL = nodes[0].stringValue()
				if imageURL.find("placeholder.jpg") != -1:
					imageURL = None
	
			XPath = """//div[@id="img_info"]/a/@href"""
			(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
			if nodes.count() == 1:
				imagePageURL = nodes[0].stringValue()
	
			XPath = """//div[@id="main"]/div[@class="person_name"]/a/@href"""
			(nodes, error) = personXHTML.nodesForXPath_error_(XPath, None)
			if nodes.count() == 1:
				wikipediaURL = nodes[0].stringValue()
			print "	extracted information from person search page"

		
		print "	image URL: " + str(imageURL)
		print "	imagePageURL: " + str(imagePageURL)
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
	htmlString = htmlString.stringByReplacingOccurrencesOfString_withString_("ADRESSE", adresse)

	imageTag = ""
	if info["imageURL"] != None and info["imagePageURL"] != None:
		imageTag = "<a class='portraitlink' href='" +  info["imagePageURL"] + "' title='Wikipedia Bildseite'><img class='portrait' style='float:right;margin-top:-3em;margin-left:0.5em;' src='" + info["imageURL"] + "' alt='" + name + "'/></a>"
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


# ohne x, der Eintrag - steht für eine zusätzliche Datei mit Nachträgen.
letters = "abcdefghijklmnopqrstuvwyz-"
#letters = "g"

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