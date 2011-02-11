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
    opentable_link = db.StringProperty()
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
        for name in scraper.get_all():
           ct += RestaurantMaker().make(name) 
           if ct > 1:
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
    def make(self, r_name):
        q = querier.Querier()
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = r_name).get()
        if rest is not None:
            return 0
        yelp_r = q.search_yelp(r_name)
        if yelp_r is None:
            return 0
        data = {}
        data['name'] = r_name
        data['opentable_link'] = q.get_opentable_link(r_name)
        data['yelp_link'] = yelp_r[0]['url']
        data['rating'] = yelp_r[0]['avg_rating']
        data['lat'] = yelp_r[0]['latitude']
        data['lng'] = yelp_r[0]['longitude']
        data['phone'] = yelp_r[0]['phone']
        data['address'] = self.stringify(yelp_r[0], ['address1', 'address2', 'address3', 'zip'])
        data['genre'] = self.stringify(yelp_r[0]['categories'], ['name']) 
        data['neighborhood'] = self.stringify(yelp_r[0]['neighborhoods'], ['name'])
        data['address'] = yelp_r[0]['address1']
        '''
        if yelp_r[0]['address2'] != '':
            data['address'] += ', ' + yelp_r[0]['address2']
        if yelp_r[0]['address3'] != '':
            data['address'] += ', ' + yelp_r[0]['address3']
        data['address'] += ', ' + yelp_r[0]['zip']
        data['neighborhood'] = ''
        for hood in yelp_r[0]['neighborhoods']:
            data['neighborhood'] += hood['name'] + ","
        data['genre'] = ''
        for cat in yelp_r[0]['categories']:
            data['genre'] = cat['name'] + ","
        '''
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
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = data['name']).get()
        if rest is None:
            rest = Restaurant()
        rest.name = data['name']
        rest.opentable_link = data['opentable_link']
        rest.yelp_link = data['yelp_link']
        rest.rating = data['rating']
        rest.neighborhood = data['neighborhood'] 
        rest.genre = data['genre']
        rest.lat = data['lat']
        rest.lng = data['lng']
        rest.address = data['address']
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

