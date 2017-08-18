from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web
import lib.minidetector
import datetime
import time
from django.core.paginator import ObjectPaginator, InvalidPage

class League(web.BaseRequestHandler):
    def get(self):
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

#form to add a new league
class LeagueNew(web.BaseRequestHandler):
    def get(self):
        sport = db.get(self.request.get('leaguesportkey'))
        sports = models.Sport.all()
        self.generate('leagueNew.html', {'sports':sports, 'leaguesportkey':sport.key})

class LeagueAdd(web.BaseRequestHandler):
    def post(self):
        name = self.request.get('name')
        description = self.request.get('description')
        sportkey = self.request.get('sportkey')
        country = self.request.get('country')
        city = self.request.get('city')
        sport = db.get(sportkey)
        #user = web.getuserprofile(self)#users.get_current_user()
        profile = web.getuserprofile(self)
        user = profile.user
        league = models.League(name=name, description=description, sport=sport, country=country, city=city, user=user)
        league.put()
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

class LeagueEdit(web.BaseRequestHandler):
    def get(self):
        league = models.League.get(self.request.get('key'))
        sports = models.Sport.all()
        self.generate('leagueEdit.html', {'league':league, 'sports':sports})

class LeagueUpdate(web.BaseRequestHandler):
    def post(self):
        league = models.League.get(self.request.get('key'))
        sport = db.get(self.request.get('sportkey'))
        league.name = self.request.get('name')
        league.description = self.request.get('description')
        league.country = self.request.get('country')
        league.city = self.request.get('city')
        league.sport = sport;
        #do a check if this user is authorised to update this league
        league.save()
        self.redirect('league?key=%s' % (league.key()))

class LeagueDelete(web.BaseRequestHandler):
    def get(self):
        league = models.League.get(self.request.get('key'))
        league.delete()
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

#the user can view a list of all leagues by sport
class LeagueListBySport(web.BaseRequestHandler):
    def get(self):
        #Detect the browser type
        browserType = None
        browserType = lib.minidetector.Middleware.process_request(self.request.headers)
        matchfilter = ""
        now = datetime.datetime.now() #up and coming fixtures
        profile = web.getuserprofile(self)
        matches = db.GqlQuery("SELECT * FROM Match WHERE matchStart > :1 ORDER BY matchStart ASC", now).fetch(5)
        leagues = None
        league = None #user preference
        newsItemCount = 0

        matchFavourites = None
        if hasattr(profile, "matchFavourites"):
            matchFavourites = db.get(profile.matchFavourites)

        sportselected = models.Sport.get(self.request.get('key'))
        leagues = db.GqlQuery('SELECT * FROM League WHERE sport = :1 ORDER BY name ASC', sportselected)
        if leagues.count() > 0:
            league = leagues[0]
            matches = models.Match.byLeagueAfterNow(leagues[0], now)

        comments = models.Comment.bySport(sportselected, 5)
        showsportlinks = 0  #track whether to show sport links on the page or not
                
        self.generate('leagueListBySport.html', {
            'matches':matches,
            'matchFavourites':matchFavourites,
            'leagues':leagues,
            'league':league,
            'comments':comments,
            'profile':profile,
            'browserType': browserType,
            'sportselected':sportselected,
            'showsportlinks': showsportlinks,
            'matchfilter': matchfilter
            })

class LeagueAddTeamToLeague(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        league.teams.append(team.key())
        league.put()

application = webapp.WSGIApplication(
    [('/league', League),
        ('/leagueAdd', LeagueAdd),
        ('/leagueNew', LeagueNew),
        ('/leagueEdit', LeagueEdit),
        ('/leagueDelete', LeagueDelete),
        ('/leagueUpdate', LeagueUpdate),
        ('/leagueListBySport', LeagueListBySport),
        ('/leagueAddTeamToLeague', LeagueAddTeamToLeague)
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()