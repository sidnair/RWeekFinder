import re
from google.appengine.ext import webapp
import cgi

register = webapp.template.create_template_register()

def normalize(value):
    value = value.replace(' ', '').lower()
    value = re.sub(' |&|<|>', '', value)
    return value

def clean_link(value):
    value = value.replace('https//', '')
    return value
 
register.filter(normalize)
