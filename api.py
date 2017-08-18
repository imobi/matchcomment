from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web
import rest
from django.utils import simplejson
import datetime
import time
from google.appengine.api import memcache

# check 
# http://skonieczny.pl/blog/it-should-just-work/post/2009/04/30/json-serialization-of-google-app-engine-models/

class Api(web.BaseRequestHandler):
    def get(self):
        self.generate('api.html', {})

#Get all sports by default and return json object, accept parameters for filtering results
class SportHandler(web.BaseRequestHandler):
    def get(self):
        sports = self.get_sports()
        results = sports.fetch(10) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        output = '{"sports":' + GqlEncoder().encode(results) + '}'
        self.response.out.write(output)

    def get_sports(self):
        sports = memcache.get("sports")
        if sports is not None:
            return sports
        else:
            sports = models.Sport.all()
            if not memcache.add("sports", sports, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return sports

#Get all leagues by default and return json object, accept parameters for filtering results
class LeagueHandler(web.BaseRequestHandler):
    def get(self):
        leagues = self.get_leagues()
        results = leagues.fetch(10) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        output = '{"leagues":' + GqlEncoder().encode(results) + '}'
        self.response.out.write(output)

    def get_leagues(self):
        leagues = memcache.get("leagues")
        if leagues is not None:
            return leagues
        else:
            leagues = models.League.all()
            if not memcache.add("leagues", leagues, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return leagues

#Get all teams by default and return json object, accept parameters for filtering results
class TeamHandler(web.BaseRequestHandler):
    def get(self):
        teams = self.get_teams()
        results = teams.fetch(10) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        output = '{"teams":' + GqlEncoder().encode(results) + '}'
        self.response.out.write(output)

    def get_teams(self):
        teams = memcache.get("teams")
        if teams is not None:
            return teams
        else:
            teams = models.Team.all()
            if not memcache.add("teams", teams, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return teams

#Get all matches by default and return json object, accept parameters for filtering results
class MatchHandler(web.BaseRequestHandler):
    def get(self):
        matches = self.get_matches()
        results = matches.fetch(10) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        output = '{"matches":' + GqlEncoder().encode(results) + '}'
        self.response.out.write(output)

    def get_matches(self):
        matches = memcache.get("matches")
        if matches is not None:
            return matches
        else:
            matches = models.Match.all()
            if not memcache.add("matches", matches, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return matches

#Get all comments by default and return json object, accept parameters for filtering results
class CommentHandler(web.BaseRequestHandler):
    def get(self):
        comments = self.get_comments()
        results = comments.fetch(100) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        #output = '{"comments":' + GqlEncoder().encode(results) + '}' throws an error
        #self.response.out.write(output)
        self.response.out.write(simplejson.dumps([property.to_dict() for property in results]))

    def get_comments(self):
        comments = memcache.get("comments")
        if comments is not None:
            return comments
        else:
            comments = models.Comment.all()
            if not memcache.add("comments", comments, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return comments

#Get all profiles by default and return json object, accept parameters for filtering results
class ProfileHandler(web.BaseRequestHandler):
    def get(self):
        profiles = self.get_profiles()
        results = profiles.fetch(10) #if u take this out it breaks
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        #output = '{"profiles":' + GqlEncoder().encode(results) + '}' throws an error
        #self.response.out.write(output)
        self.response.out.write(simplejson.dumps([property.to_dict() for property in results]))

    def get_profiles(self):
        profiles = memcache.get("profiles")
        if profiles is not None:
            return profiles
        else:
            profiles = models.Profile.all()
            if not memcache.add("profiles", profiles, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return profiles

class GqlEncoder(simplejson.JSONEncoder): 

    """Extends JSONEncoder to add support for GQL results and properties. 

    Adds support to simplejson JSONEncoders for GQL results and properties by 
    overriding JSONEncoder's default method. 
    """ 

    # TODO Improve coverage for all of App Engine's Property types. 

    def default(self, obj): 

        """Tests the input object, obj, to encode as JSON.""" 

        if hasattr(obj, '__json__'): 
            return getattr(obj, '__json__')() 

        if isinstance(obj, db.GqlQuery): 
            return list(obj) 

        elif isinstance(obj, db.Model): 
            properties = obj.properties().items() 
            output = {} 
            for field, value in properties: 
                output[field] = getattr(obj, field) 
            return output 

        elif isinstance(obj, datetime.datetime): 
            output = {} 
            fields = ['day', 'hour', 'microsecond', 'minute', 'month', 'second', 'year'] 
            methods = ['ctime', 'isocalendar', 'isoformat', 'isoweekday', 'timetuple'] 
            for field in fields: 
                output[field] = getattr(obj, field) 
            for method in methods: 
                output[method] = getattr(obj, method)() 
            output['epoch'] = time.mktime(obj.timetuple()) 
            return output 

        elif isinstance(obj, time.struct_time): 
            return list(obj) 

        elif isinstance(obj, users.User): 
            output = {} 
            methods = ['nickname', 'email', 'auth_domain'] 
            for method in methods: 
                output[method] = getattr(obj, method)() 
            return output 

        return simplejson.JSONEncoder.default(self, obj) 
    
application = webapp.WSGIApplication(
    [('/apiSport', SportHandler),
    ('/apiLeague', LeagueHandler),
    ('/apiTeam', TeamHandler),
    ('/apiMatch', MatchHandler),
    ('/apiComment', CommentHandler),
    ('/apiProfile', ProfileHandler),    
    ('/api', Api),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()