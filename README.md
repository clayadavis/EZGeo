#EZGeo
##A python package for geocoding cities, states, and countries from unstructured location strings.
###Version: 0.11

##Description

Coming up with a rough estimate of a user's location (city, state, or country) is an important part of social media research.  For some social networks, such as Twitter, precise location information is available via geotags that have been embedded by a mobile device.  Unfortunately, only a tiny fraction of users have this feature available and enabled.  A much larger percentage of users specify a less-specific location in an unstructured, user-provided location field.  This field may only be resolvable up to the country, state/province, or city level.  However, this level of detail is often sufficient for generating aggregate demographic data.

EZGeo attempts to resolve a query string representing a geographic location, anywhere in the world, in any language.  It does this using multiple data sources, including:
1) OpenStreetMaps Nominatim API
2) Hand-built gazette of distinctive city and country nicknames
3) Blacklist of common "fake" locations

After successfully resolving a query string, the algorithm will return as much of the following information as possible: latitude/longitude, city, state/state code, and country/country code.  The information is returned as a JSON data structure, as specified in the "Usage" section.

EZGeo favors precision over recall.  In other words, the algorithm is designed to minimize false positives, and only return a location if we are very sure.

##Usage

EZGeo requires Python 2.7.6 or greater, and the simplejson library.  There is no installer or setup script at the moment - simply copy the source files into your project.

To run EZGeo, simply import the module and run the resolve_location_string function:

import ezgeo
location_json = ezgeo.resolve_location_string(<location>, <?verbose>)

<location> is the location string to be queried, and <?verbose> is an optional parameter for printing details about how EZGeo attempted to resolve your query.  <location> can be an ASCII or Unicode string in any language.  The function returns structured location data in the JSON format, as follows:

    {
        'latitude' : <latitude>,
        'longitude' : <longitude>,
        'city' : <city>,
        'state',  : <state>,
        'statecode' : <statecode>,
        'country' : <country>,
        'countrycode' : <countrycode>
    }
    
EZGeo will attempt to resolve the query string as specifically as possible.  If possible, it will return a city or town.  If it cannot resolve to the city or town level, it will return a state and statecode.  If it cannot find a state, it will attempt to find a country.  Any unresolvable fields will be left blank.  Therefore, a query that cannot be resolved at all will return a JSON structure with all of the fields blank.  EZGeo will return an approximate latitude/longitude based on the centroid of the most specific location found.

##Resolution Algorithm

EZGeo begins by cleaning the string, removing leading and trailing whitespace, and converting any newline characters to spaces.  It then performs the following steps, returning the appropriate data structure when a match is finally found:

1) Attempt to find GPS coordinates in the string.  If found, attempt to resolve the coordinates using Nominatim.
2) Tokenize the query string into phrases.  A phrase is defined as a sequence of characters separated by the following delimiters: ',', '/', '\', '&', '|', ' and ', ' or ', ' to '.  Any phrases that match the blacklist (using fuzzy matching) are removed.
3) Reconstitute any remaining phrases with their original delimiters, and perform the following steps:
    3a) Try to match the string in the nickname gazette (e.g. "Philly"), and feed the standardized name (e.g. "Philadephia") into Nominatim.
    3b) Try to match the entire string in Nominatim.
    3c) Remove any (parenthesized) expressions from the string, and try to match the string in Nominatim.
4) If the entire string cannot be matched as per step 3, try matching each phrase individually using steps 3a-3c.  Of the phrases which match, return a data structure containing the most specific fields that the phrases have in common.  For example, "Houston and New York" will return a data structure containing the country "United States of America," with empty fields for the city and state.  The query "Atlanta and Japan" will return an empty data structure.

##Some Notes:
1) The blacklist fuzzy matching algorithm uses a cutoff score for deciding when to remove a phrase.  Phrases are matched using the SequenceMatcher library, which returns a similarity score between 0.0 (completely dissimilar) and 1.0 (identical).  The cutoff score is specified by BLACKLIST_CUTOFF in ezgeo.py, with a default value of 0.8.

2) The whitelist contains common nicknames for the largest cities and countries.  We've taken care to only use unique nicknames for cities and countries.  Many cities have official, generic nicknames such as "The River City" - these have been omitted because they cannot be reliably resolved to any particular city.  Feel free to add any other _unique_ nicknames you might know of.

##Ideas for Improvement:
1) Limiting Nominatim to only return matches that resolve to a city, town, country, state, province, or territory.
2) Maintaining a local gazette of the most popular locations, in JSON format, and only query the Nominatim API as a fallback measure.
3) Utilize more advanced matching techniques with said gazette, using regular expressions, feature classifiers, etc.
