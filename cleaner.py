import rweekfinder
import logging
import scraper
import querier
import cgi
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class DataCleaner(webapp.RequestHandler):

    def get(self):
        restaurants_query = rweekfinder.Restaurant.all().order('-date')
        for rest in scraper.get_all():
            self.make(rest)
        self.redirect('/'); 

    def getMeals(self, day, dict):
        if day in dict:
            if 'lunch' in dict[day] and 'dinner' in dict[day]:
                return 'Lunch and Dinner'
            elif 'lunch' in dict[day]:
                return 'Lunch'
            if 'dinner' in dict[day]:
                return 'Dinner'
        return ''

    def make(self, rest_data):
        r_name = rest_data['name']
        utf_name = r_name.decode('utf-8')
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = utf_name).get()
        if rest is None:
           return 
        q = querier.Querier()
        rest.ot_sun = self.getMeals('sunday', rest_data)
        rest.ot_mf = self.getMeals('monday', rest_data)
        rest.ot_genre = rest_data['cuisine']
        rest.ot_neighborhood = rest_data['neighborhood']
        if rest.ot_link is None:
            rest.ot_link = q.get_opentable_link(r_name)
        logging.info(rest.name + ' ' + rest_data['neighborhood'])
        rest.put();
        #TODO: GET G_LAT AND G_LONG
        #data['g_lat'] = yelp_r[0]['latitude']
        #data['g_lng'] = yelp_r[0]['longitude']
        return 1

    def stringify(self, hash, keys):
        s = []
        if len(keys) == 1:
            for sub in hash:
                if sub[keys[0]] and sub[keys[0]] != '':
                    s.append(sub[keys[0]])
        else:
            for key in keys:
                if hash[key] and hash[key] != '':
                    s.append(hash[key])
        s.sort()
        return ', '.join(s)
