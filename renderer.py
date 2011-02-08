import os
from google.appengine.ext.webapp import template

def render(writer, filepath, template_values = {}):
    path = os.path.join(os.path.dirname(__file__), filepath)
    writer.response.out.write(template.render(path, template_values))
