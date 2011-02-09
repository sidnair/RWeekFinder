import renderer
import querier
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Restaurant(db.Model):
    name = db.StringProperty()
    description = db.StringProperty(multiline=True)
    rating = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    yelp_link = db.StringProperty()
    opentable_link = db.StringProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        restaurants_query = Restaurant.all().order('-date')
        restaurants = restaurants_query.fetch(10)
        template_values = {
            'restaurants': restaurants
        }
        renderer.render(self, 'index.html', template_values)

class RestaurantPostHandler(webapp.RequestHandler):
    def post(self):
        name = self.request.get('name')
        q = querier.Querier()
        yelp_result = q.search_yelp(name)
        if yelp_result is not None:
            self.update({
                'name':name,
                'rating':yelp_result[0]['avg_rating']
                }, q)
        else:
            #no results found
            pass
        self.redirect('/')

    def update(self, data, q):
        #update existing query rather than making a totally new one
        rest = db.GqlQuery("SELECT * FROM Restaurant WHERE name = :name", name = self.request.get('name')).get()
        if rest is None:
            rest = Restaurant()
        rest.name = data['name']
        rest.opentable_link = q.get_opentable_link(data['name'])
        rest.rating = data['rating']
        rest.put()

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/new', RestaurantPostHandler)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


