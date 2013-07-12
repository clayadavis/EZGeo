#This is a demo of a small, self-contained geocoder method I wrote.
#It returns results in a standard format, suitable for comparing across
#  the different APIs.

from geocoder import geocode
import pprint

prettyPrint = pprint.PrettyPrinter(indent=4).pprint

#Three types of query: lat/lon, place name, location name
queries = ['40.714224,-73.961452', 'Indiana University', 'Beijing']

for query in queries:
    print "Press <enter> to send query \"%s\"" % query
    raw_input()
    # We can query different sites with the same query in order to compare:
    G = geocode(query, site='google')
    B = geocode(query, site='bing')
    Y = geocode(query, site='yahoo')
    # You can explicitly tell yahoo that you're giving it a place name,
    # to do so use site='yahoo_n'
    # N = geocode(query, site='yahoo_n')
    N = ''

    # Each of these objects returned are dicts with the same keys.
    print 'Query:', query
    print 'Google:'
    prettyPrint(G)
    print ''
    print 'Bing:'
    prettyPrint(B)
    print ''
    print 'Yahoo:'
    prettyPrint(Y)
    prettyPrint(N)



