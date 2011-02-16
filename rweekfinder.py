import logging
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

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                      #('/findrestaurant', RestaurantSearchHandler),
                                      #('/addrestaurant', RestaurantPostHandler),
                                      #('/addall', Adder)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

