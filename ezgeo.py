# Module for resolving location fields from Twitter to as specific of a location as possible.  Returns structured location information in JSON.

import geocoder
import re
import pprint
from unihandecode import Unihandecoder

prettyPrint = pprint.PrettyPrinter(indent=4).pprint

# Encodes string in utf-8 and makes substitutions (todo: from blacklist?)
def clean_location_string(locstr):
    # Strip all possible newline codes
    locstr = locstr.join(locstr.splitlines())
    locstr = locstr.strip()

    # Replace certain character sequences no matter where they appear in the query.
    substitutions = {
    '\t': ' ', 
    '\r': ' ',
    '\n': ' ',  
    ';)': '',
    ':)': '',
    'q8': 'kuwait',
    '\xe2\x9c\x94verified Account':'' 
    }
    
    for (k,v) in substitutions.items():
        if k in locstr.lower():
            locstr = locstr.lower().replace(k,v)
    
    # Replace query if it matches a blacklist token in it's entirety
    locstr = blacklist_token_replace(locstr)
    
    return locstr

# Maps certain tokens to appropriate substitutions (case-insensitive).  To remove tokens entirely, we map them to null strings.
def blacklist_token_replace(token):
    blacklist = {
    'ksa':'saudi',
    'heaven':'', 
    'earth':'', 
    'world':'',
    'everywhere':'', 
    'bieberland': '',
    'bieberlandia': '',
    'narnia': '',
    'in your dreams': '',
    'spaceship': '',
    'narnia': '',
    'universe': '',
    'on the moon': '',
    'mother earth': '',
    'the dance floor': '',
    't-dot': 'canada',
    'london town': 'united kingdom',
    'lion city': 'singapore',
    'philly': 'united states of america',
    'u.s.a.': 'united states of america',
    'nyc': 'united states of america',
    'atl': 'united states of america',
    'dc': 'united states of america',
    'la': 'united states of america',
    'jpn': 'japan'
    }
    
    if token.lower() in blacklist.keys():
        token = blacklist[token.lower()]
        
    # Eliminate tokens which are pure numbers    
    regex = re.compile(r'\d+$')
    if regex.match(token.lower()):    
        token = ''
        
    return token
    
# Tries to resolve a location string to a particular country.  Returns summary information on location if found.  
# Uses OSM Nominatim API for natural language, and Yahoo API for lat/lon
def resolve_location_string(locstr, lang='en', verbose=False):
    # Return null object for empty locations
    if locstr == None or locstr == '':
        return None
    
    G = None
    
    # Clean location string and make appropriate substitutions
    locstr = clean_location_string(locstr)
    
    # First step: attempt to run query directly
    try:
        G = geocoder.geocode(locstr,site='osm')
        if G['countrycode']:
            return G
    except ValueError:
        pass
    
    # Second step: attempt to run query as a lat/lon through yahoo
    try:
        # If it's a lat/lon, go ahead and put it through yahoo.
        suffix = locstr.split(':')[-1]
        (lat,lon) = [float(x) for x in suffix.strip('( )').split(',')]
        reverse = True
        query = "%s,%s" % (lat, lon)
        if verbose:
            print "* Re-checking %s" % repr(query)
        G = geocoder.geocode(query,site='yahoo')
        if G['countrycode']:
            return G
    except ValueError:
        pass

    # Third step: attempt to run query, removing any (parenthesized) expressions
    paren_regex = "\(.+?\)"
    noparens = re.sub(paren_regex,'',locstr)

    if noparens != locstr:
        if verbose:
            print "* Removing parenthetical expression: \"%s\" -> \"%s\"" % (repr(noparens), repr(locstr))
        try:
            G = geocoder.geocode(noparens, site='osm')
            if G['countrycode']:
                if verbose:
                    print "** Resolved \"%s\" as \"%s\"" % (repr(locstr), repr(noparens))
                return G
        except:
            pass    
    
    #Fourth step: attempt to break query into tokens, and run tokens individually
    #If all resolvable tokens match to the same country, then return this country 
    # TODO: In this case, strip out any info more specific than country name and location
    if verbose:
        print "* Splitting \"%s\"." % (repr(noparens))
    
    # Split on all possible delimiters
    tokens = re.split(',|/|\\\\|&|\|| and | or | to ', noparens)
    matched_country = None
    for token_ws in tokens:
        current_match = None
        # Strip whitespace from tokens and replace certain tokens with empty string
        token = blacklist_token_replace(token_ws.strip())
        
        if (token != ''):
            try:
                # First, try to directly resolve the token
                G = geocoder.geocode(token, site='osm')
                if G['countrycode']:
                    if verbose:
                        print "** Resolved \"%s\" as \"%s\"" % (repr(noparens), repr(token))
                    current_match = G['countrycode']
                    if (matched_country != None and matched_country != current_match):
                        return None
                    else:
                        matched_country = current_match
                        continue
            except:
                pass
            
            # If token doesn't match, try to match transliterated version
            try:
                # First, try to directly resolve the token
                print "Transliterating %s (lang=%s)" % (repr(token), lang)
                # WARNING: this library potentially has an infinite loop...
                unihandecoder = Unihandecoder(lang)
                G = geocoder.geocode(unihandecoder.decode(token), site='osm')
                if G['countrycode']:
                    if verbose:
                        print "** Resolved \"%s\" as \"%s\"" % (repr(noparens), unihandecoder.decode(token))
                    current_match = G['countrycode']
                    if (matched_country != None and matched_country != current_match):
                        return None
                    else:
                        matched_country = current_match
                        continue
            except:
                pass        
    return G
        
