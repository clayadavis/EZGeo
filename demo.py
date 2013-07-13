# Demos resolving various location strings using resolve_locations
import resolve_locations

#Three types of query: lat/lon, place name, location name
queries = ['Japan', 'TX', 'Mother Earth', u'\u6771\u4eac', 'Las Vegas', '40.714224,-73.961452', 'Indiana University', 'Beijing']

for query in queries:
    print "Press <enter> to send query \"%s\"" % repr(query)
    raw_input()
    try:
        location = query         
        if location and location != "":
            try:
                location_clean = resolve_locations.clean_location_string(location)
                details = resolve_locations.resolve_location_string(location_clean)[0]
                output = location + '\t' + details['country'] + ' (' + details['countrycode'] + ')\n'
            except (TypeError, ValueError):
                output = location + '\tAmbiguous or could not be resolved.\n'

        else:
            output = 'Not specified.\n'
    except():
        output = 'Error processing document.\n'
        continue
  
    print str(output.encode('ascii', 'ignore')) 



