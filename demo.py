# Demos resolving various location strings using resolve_locations in ezgeo.py
import ezgeo

#Three types of query: lat/lon, place name, location name
queries = ['Texas, U.S.A.', 'Tokyo', 'Indiana University', 'Beijing', 'TX', u'U+798fU+5ca1U+770cU+5317U+4e5dU+5ddeU+5e02' u'\u6771\u4eac', u'\u30d0\u30cb\u30fc\u3061\u3083\u3093\u3061\u306e\u30b7\u30e3\u30ef\u30fc\u30ce\u30ba\u30eb\u306e\u5148\u7aef', 
           u'\u3093\u301c\u30fb\u30fb\u30fb\u3002\u30b1\u30c4\u3063!\uff01', 'Mother Earth', u'\u6771\u4eac', 'The Dance Floor', 'In your dreams', 'Las Vegas', '40.714224,-73.961452']

for query in queries:
    print "Press <enter> to send query \"%s\"" % repr(query)
    raw_input()
    try:
        location = query
        if location and location != "":
            try:
                details = ezgeo.resolve_location_string(location)
                output = location + '\n' + 'Results: \n'
                output += 'Lat/Lon: ' + details['latitude'] + ", " + details['longitude'] + '\n'
                output += 'City: ' + details['city'] + '\n'
                output += 'State: ' + details['state'] + '\n'
                output += 'Country: ' + details['country'] + '\n'
                output += 'Country Code: ' + details['countrycode'] + '\n'
               
            except (TypeError, ValueError):
                output = location + '\n' + 'Results: Ambiguous or could not be resolved.\n'

        else:
            output = 'Not specified.\n'
    except():
        output = 'Error processing document.\n'
        continue
  
    print str(output.encode('ascii', 'ignore')) 



