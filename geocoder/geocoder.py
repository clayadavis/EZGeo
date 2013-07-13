try:
    import json
except ImportError:
    import simplejson as json
import urllib, csv, time

#These default keys are mine, Clayton Davis. Please change them.
_Y_api = 'd02e49481fad6a5cf22b29fd9cd07ff75dc9b1e9'
_bing_api = 'AquszFQCPEdtPVCX-fMi-YodZK_YQQIgmin2GhrCibFK9GeykKTJ_V0xkeDvFJ-v'

#The following aren't loaded up until they are needed. We could change
#that if needed.
_state_lookup_table = {}
_code_to_country = {}
_country_to_code = {}

####--------------------------------------------------------------------
# This is the main function that actually does (reverse) geocoding.
def geocode(query='Yellowstone', site='google', key='', verbose=False, chop=True):
    url = geturl(query, site, key)
    #print url
    failures = 0
    while failures >= 0:
        try:
            page = urllib.urlopen(url)
            failures = -1
        except IOError,e :
            secs = 2**failures
            print e
            print "   retrying in %i seconds..." % secs
            time.sleep(secs)
            failures += 1

    s = page.read()
    J = json.loads(s)
    if site=='osm':
        if J:
            J = J[0]
        else:
            J = {}    
    J.setdefault('name', query)
    if chop: #Reprocess the response into the common format
        response = chopshop(J, site)
        return response
    else: #Return the raw JSON response dict
        return J

####--------------------------------------------------------------------    
# This function takes a query and crafts the url to submit to the 
# specified API.
def geturl(query='Yellowstone', site='bing', key=''):
    #Check if the input is a lat/lon pair
    try: 
        suffix = query.split(':')[-1]
        (lat,lon) = [float(x) for x in suffix.strip('( )').split(',')]
        reverse = True
        query = "%s,%s" % (lat, lon)
    except ValueError:
        reverse = False
        pass 
        
    if site=='google':
        site_url = 'http://maps.google.com/maps/geo?%s'
        params = {'q': query,
                  'output': 'json'
                  }
        if reverse:
            params['sensor']='false'
    
    # OpenStreetMap Nominatim API
    elif site=='osm':
        site_url = 'http://nominatim.openstreetmap.org/search?%s'
        params = {'q': query,
                  'format': 'json',
                  'addressdetails': '1',
                  'accept-language': 'en'
                  }        
            
    #----------------        
    elif site=='bing':
        if not key:
            key = _bing_api
        
        if reverse:
            site_url = 'http://dev.virtualearth.net/REST/v1/Locations/' + query + '?%s'
            params = {'key' : key}
        else:
            site_url = 'http://dev.virtualearth.net/REST/v1/Locations?%s'
            params =  {'query': query,
                       'key': key
                       }
    #----------------                    
    elif site=='yahoo':
        site_url = 'http://where.yahooapis.com/geocode?%s'
        if not key:
            key = _Y_api
        params =  {'location': query,
                   'appid': key,
                   'flags': 'J'
                   }
        if reverse:
            params['gflags'] = 'R'
    #----------------        
    elif site=='yahoo_n':
        site_url = 'http://where.yahooapis.com/geocode?%s'
        if not key:
            key = _Y_api
        params =  {'name': query,
                   'appid': key,
                   'flags': 'J'
                   }
    #----------------
    else:
        raise NameError('No such site name')
        
    url = site_url % urllib.urlencode(params)
    return url

####--------------------------------------------------------------------    
# This function takes the JSON output from the different APIs and returns
# a smaller dict with a common structure, suitable for comparison.
def chopshop(J, site, verbose=False):
    keys = [u'latitude', u'longitude', u'city', u'state', 
            u'statecode', u'country', u'countrycode'] #also name
            #u'regioncode', u'continentcode']
    resp = dict(zip(keys,['']*len(keys)))

    if site[:5]=='yahoo':
        try:
            first = J['ResultSet']['Results'][0]
        except (KeyError, IndexError):
            if verbose:
                print "No results found for %s" % J['name']
            return resp
        resp[u'name'] = J['name']  
        for k in keys:
            resp[k] = first[k]
  
    elif site == 'osm':
        try:
            address = J['address']
        except (KeyError, IndexError):
            if verbose:
                print "No results found for %s" % J['name']
            return resp
         
        resp[u'name'] = J['display_name'] 
        resp['latitude'] = J['lat']
        resp['longitude'] = J['lon']
        
        try:
            resp['city'] = address['city']
        except KeyError:
            pass
        
        resp['statecode'] = ''
        
        try:
            resp['state'] = address['state']
        except KeyError:
            pass    
        
        try:
            resp['country'] = address['country']
            resp['countrycode'] = address['country_code'] 
        except KeyError:
            pass        
        
    elif site == 'bing':
        try:
            first = J['resourceSets'][0]['resources'][0]
        except (KeyError, IndexError):
            if verbose:
                print "No results found for %s" % J['name']
            return resp
            
        resp[u'name'] = first['name'] #What is the name field, exactly?
        (resp['latitude'], resp['longitude']) = first['point']['coordinates']
        resp['city'] = first['address'].get('locality','')
        
        resp['statecode'] = first['address'].get('adminDistrict','')
        resp['state'] = lookupState(resp['statecode'])
            
        resp['country'] = first['address'].get('countryRegion','')
        resp['countrycode'] = lookupCountry(resp['country'])
        
    elif site == 'google':
        try:
            first = J['Placemark'][0]
        except (KeyError, IndexError):
            if verbose:
                print "No results found for %s" % J['name']
            return resp
            
        resp[u'name'] = J['name']
        (resp['longitude'], resp['latitude'], z) = first['Point']['coordinates']
        
        try:
            resp['city'] = first['AddressDetails']['Country']['AdministrativeArea']['Locality']['LocalityName']
        except KeyError:
            try:
                resp['city'] = first['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea']['SubAdministrativeAreaName']
            except KeyError:
                pass
        
        try:
            resp['statecode'] = first['AddressDetails']['Country']['AdministrativeArea']['AdministrativeAreaName'].upper()
            resp['state'] = lookupState(resp['statecode'])
        except KeyError:
            pass
        
        try:    
            resp['country'] = first['AddressDetails']['Country']['CountryName']
            resp['countrycode'] = first['AddressDetails']['Country']['CountryNameCode']
        except KeyError:
            pass
        
    else:
        return J
    return resp

####--------------------------------------------------------------------
# The remaining functions concern the state/country lookup tables which
# convert to and from two-letter abbreviations.
def lookupState(query):
    if not _state_lookup_table:
        _load_state_lookup_table()
        
    try:
        toreturn = _state_lookup_table[query]
    except KeyError:
        toreturn = ''
        #print "%s not in state lookup table. FIX IT!" % query
        
    return toreturn
    
def _load_state_lookup_table(fname='geo_tables/states.csv'):
    states = []
    codes = []
    table = {}
    DR = csv.DictReader(open(fname), delimiter=':', quotechar='\"') #HAS HEADER
    for d in DR:
        states.append(d['State'])
        codes.append(d['Code'])
        
    for (state, code) in zip(states, codes):
        _state_lookup_table[code] = state
        _state_lookup_table[state] = code
    
    #Manual addition that isn't in the table:
    _state_lookup_table[''] = ''
    
def lookupCountry(query):
    if not _country_to_code:
        _load_country_lookup_table()
    
    if len(query) == 2:
        table = _code_to_country
        tname = 'code-to-country'
    else:
        table = _country_to_code
        tname = 'country-to-code'

    
    try:
        toreturn = table[query]
    except KeyError:
        toreturn = ''
        print "%s not in %s table. FIX IT!" % (query, tname)
        
    return toreturn
    
def _load_country_lookup_table():
    code_country_fname='geo_tables/code_to_country.csv'
    country_code_fname='geo_tables/country_to_code.csv'
    countries = []
    codes = []
    table = {}
    
    DR = csv.DictReader(open(code_country_fname), delimiter=':', quotechar='\"') #HAS HEADER
    for d in DR:
        #data = line.split(':')
        countries.append(d['Country'])
        codes.append(d['Code'])
                
    for (country, code) in zip(countries, codes):
        _code_to_country[code] = country
        
    DR = csv.DictReader(open(country_code_fname), delimiter=':', quotechar='\"') #HAS HEADER
    for d in DR:
        #data = line.split(':')
        countries.append(d['Country'])
        codes.append(d['Code'])        
        
    for (country, code) in zip(countries, codes):
        _country_to_code[country] = code
        
    #Manual addition that isn't in the table:
    _code_to_country[''] = ''
    _country_to_code[''] = ''
