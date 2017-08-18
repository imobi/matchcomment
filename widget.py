from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import os
import models
import web
import cgi

class AllComments(web.BaseRequestHandler):
    def get(self):
        
        comments = db.GqlQuery("SELECT * FROM Comment ORDER BY time DESC LIMIT 0, 10")
        
        params = cgi.FieldStorage()
        
        self.response.headers['Content-Type'] = 'text/javascript'  
        
        if not 'callback' in params:
            print "ERROR: you must pass a callback parameter"
        else:
            jsonp = "%s ( {'html': %r } )" 
            
            template_values = {
                'comments': comments,
            }
            
            self.response.out.write(jsonp % (params['callback'].value, template.render('templates/commentsWidget.html', template_values)) )
            
#Widget Test
class WidgetTest(web.BaseRequestHandler):
    def get(self):
        self.generate('widget.html', {})
        
class CatchAll(web.BaseRequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('profile 404')

application = webapp.WSGIApplication(
    [('/widgetAllComments', AllComments),
        ('/widgettest', WidgetTest),
        ('/.*', CatchAll),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()