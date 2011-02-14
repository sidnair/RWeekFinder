import renderer
import querier
import scraper
import cgi
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

"""Load custom Django template filters"""
webapp.template.register_template_library('djangofilters')

class Restaurant(db.Model):
    name = db.StringProperty()
    #description = db.StringProperty(multiline=True)
    rating = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    yelp_link = db.StringProperty()
    yelp_id = db.StringProperty()
    ot_link = db.StringProperty()
    ot_genre = db.StringProperty()
    ot_neighborhood = db.StringProperty()
    ot_mf = db.StringProperty()
    ot_sun = db.StringProperty()
    genre = db.StringProperty()
    neighborhood = db.StringProperty()
    address = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        restaurants_query = Restaurant.all().order('-date')
        template_values = {
            'restaurants': restaurants_query
        }
        renderer.render(self, 'index.html', template_values)
        '''
        RestaurantMaker().add({
            'name':'Perilla',
            'genre':'New American',
            'neighborhood':'Ghetto',
            'opentable_link':querier.Querier().get_opentable_link('Perilla'),
            'yelp_link':'ylink',
            'rating':4.0,
            "lat": 40.7322680,
            "lng": -74.0017980',
            'address':'9 Jones Street'
            })
        '''
class Adder(webapp.RequestHandler):
    def get(self):
        self.addAll()
    
    def addAll(self):
        ct = 0
        cap = 5 
        for rest in scraper.get_all():
           ct += RestaurantMaker().make(rest)
           if ct > cap:
               self.redirect('/')
               return

class RestaurantSearchHandler(webapp.RequestHandler):
    def post(self):
        name = self.request.get('name')
        q = querier.Querier()
        yelp_result = q.search_yelp(name)
        self.response.out.write(simplejson.dumps( {
                'opentable':q.get_opentable_link(name),
                'yelp':yelp_result
                }))

class RestaurantPostHandler(webapp.RequestHandler):
    def post(self):
        RestaurantMaker().make(self.request.get('name'))

class RestaurantMaker:

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
        q = querier.Querier()
        data = {}
        data['ot_sun'] = self.getMeals('sunday', rest_data)
        data['ot_mf'] = self.getMeals('monday', rest_data)
        r_name_utf = r_name.decode('utf-8')
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = r_name_utf).get()
        if rest is not None:
            return 0
        yelp_r = q.search_yelp(r_name)
        if yelp_r is None:
            return 0
        data['name'] = r_name
        data['ot_genre'] = rest_data['cuisine']
        data['ot_neighborhood'] = rest_data['neighborhood']
        data['ot_link'] = q.get_opentable_link(r_name)
        data['yelp_link'] = yelp_r[0]['url']
        data['yelp_id'] = yelp_r[0]['id']
        data['rating'] = yelp_r[0]['avg_rating']
        data['lat'] = yelp_r[0]['latitude']
        data['lng'] = yelp_r[0]['longitude']
        data['phone'] = yelp_r[0]['phone']
        data['address'] = self.stringify(yelp_r[0], ['address1', 'address2', 'address3', 'zip'])
        data['genre'] = self.stringify(yelp_r[0]['categories'], ['name']) 
        data['neighborhood'] = self.stringify(yelp_r[0]['neighborhoods'], ['name'])
        data['address'] = yelp_r[0]['address1']
        self.add(data)
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

    def add(self, data):
        utf_name = data['name'].decode('utf-8')
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = utf_name).get()
        if rest is None:
            rest = Restaurant()
        #rest.name = data['name']
        rest.name = utf_name
        rest.ot_link = data['ot_link']
        rest.yelp_link = data['yelp_link']
        rest.rating = data['rating']
        rest.neighborhood = data['neighborhood'] 
        rest.genre = data['genre']
        rest.lat = data['lat']
        rest.lng = data['lng']
        rest.address = data['address']
        rest.ot_sun = data['ot_sun']
        rest.ot_mf = data['ot_mf']
        rest.yelp_id = data['yelp_id']
        rest.ot_genre = data['ot_genre']
        rest.ot_neighborhood = data['ot_neighborhood']
        rest.put()


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/findrestaurant', RestaurantSearchHandler),
                                      ('/addrestaurant', RestaurantPostHandler),
                                      ('/addall', Adder)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

