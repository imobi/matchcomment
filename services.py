from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from protorpc import service_handlers

import commentservice
import matchservice

# Register mapping with application.
application = webapp.WSGIApplication(
 service_handlers.service_mapping(
     [('/commentservice', commentservice.CommentService),
      ('/matchservice', matchservice.MatchService)]),
 debug=True)

  
def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()