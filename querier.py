import json
import logging
import urllib2
import urllib

"""
Gets all the required info from the web - opentable data and yelp.
"""
class Querier:
    def get_opentable_link(self, name):
        params = {
                "Appid" : "9360382F94C8616C337CDC5BBE6EA5CED7A2BDF3",
                "sources" : "web",
                "query" : name + " site:opentable.com" 
        }
        search_host = "http://api.search.live.net/json.aspx"
        path = "%s?%s" %(search_host, urllib.urlencode(params))
        data = urllib2.urlopen(path).read()
        result = json.loads(data)
        web_results = result['SearchResponse']['Web']['Results']
        if web_results is not None:
            return web_results[0]['DisplayUrl']
        else:
            return None

    def search_yelp(self, query):
        search_host = "http://api.yelp.com/business_review_search"
        params = {
                "term" : query,
                "location" : "2920 Broadway, New York, NY",
                "ywsid" : "zbLtUIhjaf-a1RKjTvtSNg",
                "cflt" : "restaurants"
                }
        path = "%s?%s" %(search_host, urllib.urlencode(params))
        data = urllib2.urlopen(path).read()
        result = json.loads(data)
        if 'businesses' not in result or len(result['businesses']) == 0:
            if result['message']['code'] != 0:
                return result['message']
            return None 
        return result['businesses']
