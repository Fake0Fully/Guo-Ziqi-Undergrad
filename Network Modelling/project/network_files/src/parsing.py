import zen
import urllib
import time
import unicodedata

# Define Flags for Parsing
PAGE_START = '<table>'
PAGE_END = '</table>'

ENTRY_START = '<a href='
ENTRY_END = '</a></td>'

TEXT_TITLE = 'Visa Information</b></td><td' # only keep texts after the title
TEXT_START = '<div align=left>' 
TEXT_END = '<a href=' # hyperlink as endpoint


G = zen.DiGraph()
urllist = []

def add_nodes(theurl,urllist):
	print '\nAnalyzing: ' + theurl
	try:
		f = urllib.urlopen(theurl)
		s = f.read()
		f.close()
	except:
		print '\tConnection Issue!'
		time.sleep(2)
		add_nodes(theurl)

	contents = s.split(PAGE_START)[2]
	contents = contents.split(PAGE_END)[0]
	
	entries = contents.split(ENTRY_START)
	entries = entries[1:]

	regions = []
	for entry in entries:
		if entry.find('regions') >= 0:
			regions.append(entry.split(ENTRY_END)[0].split('>')[1])
			entries.remove(entry)

	for i in range(len(entries)):
		entries[i] = entries[i].split(ENTRY_END)[0].split('>')
		if entries[i][1] not in G:
			urllist.append('http://www.projectvisa.com'+entries[i][0].split('"')[1])
			G.add_node(entries[i][1],data=regions[i])

# Retrieve the visa information in the entry as text
def get_information(theurl):
	f = urllib.urlopen(theurl)
	s = f.read()
	f.close()
	text = s.split(TEXT_TITLE)[1].split(TEXT_START)[1].split(TEXT_END)[0]
	return text

# Add edges to countries except for the mentioned countries in the entry
def add_edges_reverse(country):
	for i in G.nodes():
		if country!=i and text.find(i)<0 and G.has_edge(i,country)==False:
			print 'reverse edge added'
			G.add_edge(i,country)

# Skip normal split endpoint because of unexpected hyperlink
def add_edges_jump(country):
	f = urllib.urlopen(urllist[country])
	s = f.read()
	f.close()
	text = s.split(TEXT_TITLE)[1].split(TEXT_START)[1].split('</div>')[0]
	for j in range(0,G.num_nodes):
		if country!=j and text.find(G.node_object(j))>=0 and G.has_edge_(j,country)==False:
			print 'jump edge added'
			G.add_edge_(j,country)

# This function is for foreign territories whose visa requirements are the same as their mother countries'
# This function will replicate mother countries' edges to the foreign territory
def add_edges_foreign(country):
	f = urllib.urlopen(urllist[country])
	s = f.read()
	f.close()
	text = s.split(TEXT_TITLE)[1].split(TEXT_START)[1].split('</div>')[0]
	for k in G.nodes_():
		if text.find(G.node_object(k)) >= 0 and k!=country:
			for j in G.in_neighbors_(k):
				if G.has_edge_(j,country)==False:
					print 'foreign territory'
					G.add_edge_(j,country)

# The two functions below are all to parse texts that contain mixed information
# Mixed information means it lists the countries that enjoy benefits as well as those that don't
def BigTroubleMaker(id,where):
	text = get_information(urllist[id]).split('<br />')
	for i in where:
		del text[i]
	result = ''
	for i in text:
		result += i
	print 'trouble solved'
	return result
def SmallTroubleMaker(id,where):
	text = get_information(urllist[id]).split('<p>')
	for i in where:
		del text[i]
	result = ''
	for i in text:
		result += i
	print 'trouble solved'
	return result 

add_nodes('http://www.projectvisa.com/fullcountrylist.asp',urllist)

# Change node object names for better searching results
G.set_node_object('Congo, Democratic Republic of the (Zaire)','Democratic Republic of the Congo')
G.set_node_object('Congo, Republic of','Republic of Congo')
G.set_node_object('Guadeloupe (French)','Guadeloupe')
G.set_node_object('Guam (USA)','Guam')
G.set_node_object('Ivory Coast (Cote D`Ivoire)','Ivory Coast')
G.set_node_object('Martinique (French)','Martinique')
G.set_node_object('New Caledonia (French)','New Caledonia')
G.set_node_object('Polynesia (French)','Polynesia')
G.set_node_object('Timor-Leste (East Timor)','Timor-Leste')

# Lists of unions that are frequently referred to as a whole
ECOWAS = ['Benin','Burkina Faso','Gambia','Ghana','Guinea','Guinea Bissau','Ivory Coast','Liberia','Mali','Niger','Nigeria','Senegal','Sierra Leone','Togo']
Commonwealth = ['Antigua and Barbuda','Bangladesh','Botswana','Canada','Fiji','Guyana','Kenya','Malawi','Malta','Namibia','Nigeria','Rwanda','Seychelles','Solomon Islands','Saint Kitts and Nevis','Tonga','Uganda','Vanuatu','Australia','Barbados','Brunei','Cyprus','Ghana','India','Kiribati','Malaysia','Mauritius','Nauru','Pakistan','Saint Lucia','Sierra Leone','South Africa','Saint Vincent and Grenadines','Trinidad and Tobago','United Kingdom','Zambia','Bahamas','Belize','Cameroon','Dominica','Grenada','Jamaica','Lesotho','Maldives','Mozambique','New Zealand','Papua New Guinea','Samoa','Singapore','Sri Lanka','Swaziland','Tuvalu','Tanzania']
EU = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czech Republic','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden','United Kingdom']

# Lists of countries that require different methods(defined above) to parse
# The countries in the lists are identified through some flags such as 'not required','all','exempted',etc.
reverse = ['United Kingdom','Mauritius','Laos','Malaysia','Phillipines','Singapore','Hong Kong','Nicaragua','Saint Kitts and Nevis','Anguilla','Barbados','Bermuda','Haiti','Kosovo','Ecuador']
foreign_territory = ['Bouvet Island','Cayman Islands','Faroe Islands','French Guiana','Greenland','Guadeloupe','Martinique','Monaco','Mayotte','Reunion','Saint Pierre and Miquelon','Turks and Caicos Islands','Christmas Island','Cocos (Keeling) Islands','Puerto Rico']
jump = ['Montserrat','Netherlands Antilles','Virgin Islands','Svalbard and Jan Mayen Islands']
BigTrouble = {"Egypt":[5],"Nepal":[2],"Jordan":[9,12,15],"Armenia":[2],"Kenya":[3],"Tanzania":[6],"Zambia":[5,6]}
SmallTrouble = {"Zimbabwe":[2],"Bangladesh":[2],"Sri_Lanka":[2]}
all_connected = {'Madagascar','Maldives','Palau','Saint Helena','Saint Vincent and Grenadines','Samoa','Seychelles','Togo','Tuvalu'}

# Add edges
for i in range(0,G.num_nodes):
	print 'Round '+str(i)
	try:
		text = get_information(urllist[i])
	except:
		continue
	if G.node_object(i) in reverse:
		add_edges_reverse(G.node_object(i))
	elif G.node_object(i) in jump:
		add_edges_jump(i)		
	else:
		if G.node_object(i) in BigTrouble.keys():
			text = BigTroubleMaker(i,BigTrouble[G.node_object(i)])
		elif G.node_object(i) in SmallTrouble.keys():
			text = SmallTroubleMaker(i,SmallTrouble[G.node_object(i)])
		for j in range(0,G.num_nodes):
			if i!=j and text.find(G.node_object(j))>=0 and G.has_edge_(j,i)==False:
				print 'edge added'
				G.add_edge_(j,i)
		if text.find('ECOWAS')>=0:
			for k in ECOWAS:
				if G.has_edge_(G.node_idx(k),i)==False:
					print 'extra edge added'
					G.add_edge_(G.node_idx(k),i)
		if text.find(' EU ')>=0 or text.find('European Union')>=0:
			for k in EU:
				if G.has_edge_(G.node_idx(k),i)==False:
					print 'extra edge added'
					G.add_edge_(G.node_idx(k),i)
		if text.find('Commonwealth')>=0:
			for k in Commonwealth:
				if G.has_edge_(G.node_idx(k),i)==False:
					print 'extra edge added'
					G.add_edge_(G.node_idx(k),i)
# Replicate foreign territory edges
for i in range(0,G.num_nodes):
	if G.node_object(i) in foreign_territory:
		add_edges_foreign(i)
# For countries that are open to everyone
for i in range(0,G.num_nodes):
	if G.node_object(i) in all_connected:
		print 'all connected'
		for j in G.nodes():
			if j!=G.node_object(i):
				G.add_edge(j,G.node_object(i))

# Special changes made
addlist = ['Australia','France','Germany','Hong Kong','Japan','New Zealand','Switzerland','United Kingdom','United States']
group = {}
for i in G.in_neighbors('Singapore'):
	G.rm_edge(i,'Singapore')
for i in addlist:
	G.add_edge(i,'Singapore')
for i in G.nodes():
	if G.node_data(i)=='Europe' or G.node_data(i)=='North America':
		if G.has_edge(i,'Singapore')==False:
			G.add_edge(i,'Singapore')


zen.io.gml.write(G,'projectvisa.gml',write_data=(True,False),use_zen_data=(True,False))








