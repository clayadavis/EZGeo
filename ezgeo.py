# Module for resolving location fields from Twitter to as specific of a location as possible.  Returns structured location information in JSON.

import geocoder
import re
import pprint
import blacklist
import json
import os

BLACKLIST_CUTOFF = 0.8

prettyPrint = pprint.PrettyPrinter(indent=4).pprint
blacklist_words = open(os.path.dirname(__file__) + "/dictionaries/blacklist.txt").read().split('\n')
b = blacklist.Blacklist(blacklist_words)
json_data = open(os.path.dirname(__file__) + "/dictionaries/nicknames.json")
nicknames = json.load(json_data)

# Tries to resolve a location string to a particular country.  Returns summary information on location if found.  
# Uses OSM Nominatim API for natural language, and Yahoo API for lat/lon
def resolve_location_string(locstr, verbose=False):
    # Return null object for empty locations
    if locstr == None or locstr == '':
        return None
    
    G = None
    
    # Clean location string and make appropriate substitutions
    locstr = clean_location_string(locstr)

    # First step: attempt to run (unicode-removed) query as a lat/lon
    try:
        G = match_gps(locstr, verbose)
        if G['countrycode']:
            return G
    except ValueError:
        pass

    # Second,  clean string of blacklisted tokens and attempt to match entire string
    # Tokenize location string
    clean_tokens = get_relevant_tokens(locstr, verbose)
    
    print clean_tokens
    
    # Reconstitute valid tokens into a single cleaned string
    clean_locstr = ""
    for (tok, sep) in clean_tokens:
        clean_locstr += tok + sep
    if verbose:
        print "Cleaned string: " + repr(clean_locstr)
    # First, try to match entire cleaned string
    try:
        G = match_phrase(clean_locstr, verbose)
        if G['countrycode']:
            return G
    except:
        if verbose:
            print "Could not match entire phrase.  Attempting to match tokens."
        pass
    
    # Third, try to match multiple tokens individually.  If all resolvable tokens match to the same country, then return the matched dataset 
    # TODO: In this case, return the intersection of different tokens' datasets (i.e., only what they have in common).
    if (len(clean_tokens) > 1):
        if verbose:
            print "Trying to match tokens in \"%s\"." % (repr(clean_locstr))
        
        final_match = None
        for token_pairs in clean_tokens:
            tok = token_pairs[0]
            current_match = match_phrase(tok, verbose) 
            if verbose:
                print "Trying to match " + repr(tok)
            # First, try to directly resolve the token
            if current_match['country']:
                if verbose:
                    print "** Resolved token \"%s\" to %s" % (repr(tok), repr(current_match['country']))
            
            # If we haven't made a match before
            if (final_match != None):
                # If the lat/lon don't match, clear the lat/lon
                if (current_match['latitude'] != ""):
                    if (not (current_match['latitude'] == final_match['latitude'] and current_match['longitude'] == final_match['longitude'])):
                        final_match['latitude'] = final_match['longitude'] = ""
                # If the city doesn't match, clear the city
                if (current_match['city'] != ""):
                    if (current_match['city'] != final_match['city']):
                        final_match['city'] = ""
                # If the state doesn't  match, clear the state
                if (current_match['state'] != ""):
                    if (current_match['state'] != final_match['state']):
                        final_match['state'] = final_match['statecode'] = ""
                # If the country doesn't match, clear the country and return
                if (current_match['country'] != "" ):
                    if (current_match['country'] != final_match['country']):
                        final_match['country'] = final_match['countrycode'] = ""
                        return final_match
            else:
                final_match = current_match

        return final_match

    return None

# Converts to lowercase, removes emoticons, and standardizes some common whitespace items
def clean_location_string(locstr):
    locstr = locstr.strip().lower()

    # Replace certain character sequences no matter where they appear in the query.
    substitutions = {
    '\t': ' ', 
    '\r': ' ',
    '\n': ' ',  
    ';)': '',
    ':)': ''
    }
    
    for (k,v) in substitutions.items():
        if k in locstr.lower():
            locstr = locstr.lower().replace(k,v)
    
    return locstr

# Convert a string into a dictionary of relevant tokens, deleting any blacklisted tokens.  
# Tokens are defined as being separated by any of: [,/\&| and or to]
# Returns an array of (token,separator) pairs.
def get_relevant_tokens(locstr, verbose=False):
    token_pairs = []
    # Split on all possible delimiters
    tokens_and_separators = re.split('(,|/|\\\\|&|\|| and | or | to )', locstr)
    if verbose:
        print tokens_and_separators
    tokens = tokens_and_separators[0:len(tokens_and_separators):2]
    print tokens
    # Map non-empty and non-numeric tokens to their separators
    re_num = re.compile(r'\d+$') 
    for idx, tok in enumerate(tokens):
        if (tok != ""  and not re_num.match(tok)):
            score, match = b.checkWord(repr(tok))   #Check the non-unicode version of the string
            if score < BLACKLIST_CUTOFF:
                if (2*idx+1 < len(tokens_and_separators)):
                    sep =  tokens_and_separators[2*idx+1]
                else:
                    sep = ""    
                token_pairs.append((tok.strip(), sep))
            else:
                if verbose:
                    print "Found blacklisted token: %s as %s, score %s" % (repr(tok), repr(match), str(score))
        else:
            if verbose:
                print "Found numeric or null token: " + tok        
    return token_pairs
            
def match_phrase(phrase, verbose=False):
    # First step: attempt to map nicknames to standard place names
    if (phrase in nicknames):
        if verbose:
            print "Resolved nickname \"%s\" as \"%s\": " % (repr(phrase), repr(nicknames[phrase]))
        phrase = nicknames[phrase]

    # Second step: attempt to match mapped string in Nominatim
    try:
        G = geocoder.geocode(phrase,site='osm')
        if G['countrycode']:
            return G
    except ValueError:
        pass

    # Third step: attempt to run query, removing any (parenthesized) expressions
    paren_regex = "\(.+?\)"
    noparens = re.sub(paren_regex,'',phrase)

    if noparens != phrase:
        if verbose:
            print "* Removing parenthetical expression: \"%s\" -> \"%s\"" % (repr(noparens), repr(phrase))
        try:
            G = geocoder.geocode(noparens, site='osm')
            if G['countrycode']:
                if verbose:
                    print "** Resolved \"%s\" as \"%s\"" % (repr(phrase), repr(noparens))
                return G
        except ValueError:
            pass    

    return G
        
def match_gps(locstr, verbose=False):
    suffix = locstr.split(':')[-1]
    (lat,lon) = [float(x) for x in suffix.strip('( )').split(',')]
    reverse = True
    query = "%s,%s" % (lat, lon)
    if verbose:
        print "Trying to match string \"%s\" as lat/lon..." % repr(query)
    return geocoder.geocode(query,site='osm')
        