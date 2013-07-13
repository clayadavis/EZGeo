# Module for resolving location fields from Twitter to as specific of a location as possible.  Returns structured location information in JSON.

import geocoder
import re
import pprint

prettyPrint = pprint.PrettyPrinter(indent=4).pprint

# Encodes string in utf-8 and makes substitutions (todo: from blacklist?)
def clean_location_string(locstr):
    # Must encode all locations in utf-8 before sending through a URL-based API
    location_unicode = locstr.encode('utf-8')

    # Strip all possible newline codes
    location_unicode = location_unicode.join(location_unicode.splitlines())

    if location_unicode.lower().strip() == 'toronto':
        location_unicode = 'Toronto, ON'

    # TODO: might be done more efficiently with a regex?
    substitutions = {'ksa':'saudi', 'heaven':'', 'earth':'', 'world':'',
            '\xe2\x9c\x94Verified Account':'', 'everywhere':'', '\t': ' '}
    for (k,v) in substitutions.items():
        if k in location_unicode.lower():
            location_unicode = location_unicode.lower().replace(k,v)
    
    return location_unicode

# Tries to resolve a location string to a particular country.  Returns summary information on location if found.  
# Uses OSM Nominatim API for natural language, and Yahoo API for lat/lon
def resolve_location_string(locstr, verbose=False):
    if locstr == None:
        return (None, None)

    G = geocoder.geocode(locstr,site='osm')
    if G['countrycode']:
        return (G,'osm')

    try:
        # If it's a lat/lon, go ahead and put it through yahoo.
        suffix = locstr.split(':')[-1]
        (lat,lon) = [float(x) for x in suffix.strip('( )').split(',')]
        reverse = True
        query = "%s,%s" % (lat, lon)
        if verbose:
            print "* Re-checking %s" % query
        G = geocoder.geocode(query,site='yahoo')
        if G['countrycode']:
            return (G,'yahoo')
    except ValueError:
        pass

    paren_regex = "\\(.+?\\)"
    noparens = re.sub(paren_regex,'',locstr)

    if noparens != locstr:
        if verbose:
            print "* Removing parenthetical expression from \"%s\"" % locstr
        G = geocoder.geocode(noparens, site='osm')
        if G['countrycode']:
            if verbose:
                print "** Resolved \"%s\" as \"%s\"" % (locstr, noparens)
            return (G,'osm')
        #for matches in re.findall(paren_regex,locstr):

    for c in ['/','\\','&','|', ' and ', ' or ']: 
    #Probably don't need colon here as it splits on that in the geocode code.
        if c in locstr:
            if verbose:
                print "* Splitting \"%s\" on \"%s\"." % (locstr,c)
            pieces = locstr.split(c)
            for part in pieces:
                s = part.strip()
                G = geocoder.geocode(s, site='osm')
                if G['countrycode']:
                    if verbose:
                        print "** Resolved \"%s\" as \"%s\"" % (locstr, s)
                    return (G,'osm')
    if verbose:
        print "Couldn't resolve %s." % locstr
    return (None, None)