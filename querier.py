import httplib
import json
import logging
import socket
import time
import urllib2
import urllib

"""
Gets all the required info from the web - opentable data and yelp.
"""
class Querier:
    def get_opentable_link(self, name):
        #boss search for "site:opentable.com :name"
        return 'foo'
    
    def search_yelp(self, query):
        search_host = "http://api.yelp.com/business_review_search"
        search_path = ""
        params = {
                'term' : query,
                "location" : "2920 Broadway, New York, NY",
                "ywsid" : "zbLtUIhjaf-a1RKjTvtSNg"
                }
        path = "%s?%s" %(search_path, urllib.urlencode(params))
        data = urllib2.urlopen(search_host + path).read()
        result = json.loads(data)
        if 0 not in result['businesses']:
            return None
        return result['businesses']
"""
        return {'rating':path}
        try:
            c.request('GET', path)
            r = c.getresponse()
            data = r.read()
            c.close()
            try:
                result = json.loads(data)
            except ValueError:
                return None
            if 0 not in result['businesses']:
                return None
        first_result = result['businesses'][0]
        curated_result = {
                'rating':first_result['avg_rating'],
                'neighborhood':first_result['neighborhoods'][0]['name']
                }
        return curated_result
        except (httplib.HTTPException, socket.error, socket.timeout), e:
            logging.error("search() error: %s" %(e))
            return None 
            """
