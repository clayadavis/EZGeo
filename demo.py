# Demos resolving various location strings using resolve_locations in ezgeo.py
import ezgeo
from unihandecode import Unihandecoder

#Three types of query: lat/lon, place name, location name
queries = [('Spangfield, MA', 'en'),
           ('Houston and The Big Apple', 'en'),
           ('Atlanta to Japan', 'en'),
           ('Norge, Skien', 'en'),
           ('iPhone: 42.717816,-88.998709', 'en'),
           ('Sin City', 'en'),
           (u'\u3093\u301c\u30fb\u30fb\u30fb\u3002\u30b1\u30c4\u3063!\uff01','ja'),
           (u'\u6771\u4eac', 'ja'),
           (u'\u30d0\u30cb\u30fc\u3061\u3083\u3093\u3061\u306e\u30b7\u30e3\u30ef\u30fc\u30ce\u30ba\u30eb\u306e\u5148\u7aef', 'ja'),
           ('Tokyo', 'en'),
           ('Texas, U.S.A.', 'en'),
           ('Indiana University', 'en'),
           ( 'Beijing', 'en'),
           ('TX', 'en'),
           ('Mother Earth', 'en'),
           ('The Dance Floor', 'en'),
           ('In your dreams', 'en'),
           ('Las Vegas', 'en'),
           ('40.714224,-73.961452','en')]

for query in queries:
    print "Press <enter> to send query \"%s\"" % repr(query)
    raw_input()
    try:
        if query[0] != "" and query[1] != "":
            output = '---- Results ----\n'
            #try:
            locstr = query[0]
            lang = query[1]              
            # First try to resolve string in native language
            details = ezgeo.resolve_location_string(locstr, True)
            # If that fails, try transliterating (if the language is not English)
            if (not details or not details['countrycode']) and lang != 'en':        
                # WARNING: this library potentially has an infinite loop...
                print "Transliterating %s (lang=%s)" % (repr(locstr), lang)  
                unihandecoder = Unihandecoder(lang)
                locstr = unihandecoder.decode(locstr)
                details = ezgeo.resolve_location_string(locstr, True)
            output += 'Queried string: ' + repr(locstr) + '\n'
            
            if details and details['countrycode']:
                output += 'Lat/Lon: ' + details['latitude'] + ", " + details['longitude'] + '\n'
                output += 'City: ' + details['city'] + '\n'
                output += 'State: ' + details['state'] + '\n'
                output += 'Country: ' + details['country'] + '\n'
                output += 'Country Code: ' + details['countrycode'] + '\n'
            else:
                output += 'Ambiguous or could not be resolved.\n'                             

        else:
            output = 'Not specified.\n'
    except():
        output = 'Error processing document.\n'
        continue
  
    print str(output.encode('ascii', 'ignore')) 



