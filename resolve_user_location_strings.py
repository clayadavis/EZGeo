import sys, os, datetime, time, re
from datetime import timedelta
import datetime
import truthy_twitter
from keyword_computer import keyword_computer
from sparkline_creator import create_meme_sparklines
from system_stats import track_status
import simplejson as json
from contextlib import closing, nested
from common.mysql import get_mysql
import geocoder
import update_user_locations

def get_unresolved_user_locations(db):
    print "Getting unresolved user locations..."
    query = """
        SELECT screen_name, location_string FROM users
        WHERE location_string IS NOT NULL
            AND location_string NOT IN (
                SELECT location_string FROM locations)
        """
    tic = time.time()
    sn_locstr_pairs = []
    with closing(db.cursor()) as c:
        c.execute(query)
        sn_locstr_pairs = c.fetchall()
    toc = time.time()

    print "Fetched %i locations to resolve in %f seconds." \
            %(len(sn_locstr_pairs), toc-tic)
    
    return sn_locstr_pairs

def resolve_user_locations(pairs, store_empty=False):
    print "Resolving %i user locations..." % len(pairs)
    output_tuples = []
    for pair in pairs:
        (sn, locstr) = pair
        (G, api) = resolve_location_string(locstr, verbose=True)
        if G or store_empty:
            output_tuples.append((sn, locstr, G, api))

    return output_tuples
        
def clean_location_string(locstr):

    if locstr.lower().strip() == 'toronto':
        locstr = 'Toronto, ON'

    substitutions = {'ksa':'saudi', 'heaven':'', 'earth':'', 'world':'',
            '\xe2\x9c\x94Verified Account':'', 'everywhere':''}
    for (k,v) in substitutions.items():
        if k in locstr.lower():
            locstr = locstr.lower().replace(k,v)
    
    return locstr

def resolve_location_string(locstr, verbose=False):
    locstr = clean_location_string(locstr)
    G = geocoder.geocode(locstr,site='bing')
    if G['countrycode']:
        return (G,'bing')

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
        G = geocoder.geocode(noparens, site='bing')
        if G['countrycode']:
            if verbose:
                print "** Resolved \"%s\" as \"%s\"" % (locstr, noparens)
            return (G,'bing')
        #for matches in re.findall(paren_regex,locstr):

    for c in ['/','\\','&','|', ' and ', ' or ']: 
    #Probably don't need colon here as it splits on that in the geocode code.
        if c in locstr:
            if verbose:
                print "* Splitting \"%s\" on \"%s\"." % (locstr,c)
            pieces = locstr.split(c)
            for part in pieces:
                s = part.strip()
                G = geocoder.geocode(s, site='bing')
                if G['countrycode']:
                    if verbose:
                        print "** Resolved \"%s\" as \"%s\"" % (locstr, s)
                    return (G,'bing')
    if verbose:
         print "Couldn't resolve %s." % locstr
    return (None, None)


def save_user_locations(intuples, db): 
#intuples are (sn,locstr,geocode_object,api)
    for tup in intuples:
        (sn, locstr, G, api) = tup

        if G['countrycode'] == 'US':
            lcode = 'US-%s' % G['statecode']
        else:
            lcode = G['countrycode']

        with closing(db.cursor()) as c:
            try:
                if type(locstr) == unicode:
                    strtostore = locstr.encode('utf8')
                else:
                    strtostore = locstr
                c.execute("""
                    REPLACE INTO locations
                        (location_string, location_code, api_used, geodata_json)
                    VALUES (%s,%s,%s,%s)
                    """, (strtostore, lcode, api,json.dumps(G)))
            except Exception, e:
                print "Error storing location data %s:" % locstr 
                print Exception, e


if __name__ == '__main__':

    with closing(get_mysql(db_name='truthy_new')) as db:
        if True:
            sn_locstr_pairs = get_unresolved_user_locations(db)
        else:
            sn_locstr_pairs = []

        numatonce = 100
        numsaved = 0
        numtosave = len(sn_locstr_pairs)

        choppedlist = update_user_locations.chopList(sn_locstr_pairs, numatonce)
        for sublist in choppedlist:
            tuples = resolve_user_locations(sublist)
            save_user_locations(tuples, db)
            numsaved += len(sublist)
            print "%i of %i records saved." % (numsaved, numtosave)

        
