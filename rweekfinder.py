import renderer
import querier
import scraper
import cgi
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Restaurant(db.Model):
    name = db.StringProperty()
    #description = db.StringProperty(multiline=True)
    rating = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    yelp_link = db.StringProperty()
    opentable_link = db.StringProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        restaurants_query = Restaurant.all().order('-date')
        restaurants = restaurants_query.fetch(100)
        template_values = {
            'restaurants': restaurants
        }
        renderer.render(self, 'index.html', template_values)

class Adder(webapp.RequestHandler):
    def get(self):
        self.addAll()
    
    def addAll(self):
        ct = 0
        for name in scraper.get_all():
           ct += RestaurantMaker().make('Perilla') 
           if ct > 0:
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
        r_name = 'Perilla'
        q = querier.Querier()
        #update existing query rather than making a totally new one
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = r_name).get()
        if rest is None:
            rest = Restaurant()
        else:
            return 0 
        yelp_r = q.search_yelp(r_name)
        if yelp_r is None:
            return 1
        rest.name = r_name
        rest.opentable_link = q.get_opentable_link(r_name)
        rest.yelp_link = yelp_r[0]['url']
        rest.rating = yelp_r[0]['avg_rating']
        #for each thing in data, add the trait
        rest.put()
        return 1

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

