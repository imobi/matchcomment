from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web

class Admin(web.BaseRequestHandler):
    def get(self):
        self.generate('admin.html', {})

class SportAll(web.BaseRequestHandler):
    def get(self):
        sports = models.Sport.all()
        self.generate('sportHome.html', {'sports':sports})

class ProfileAll(web.BaseRequestHandler):
    def get(self):
        totalcomments = models.Comment.count_all(models.Comment)
        totalusers = models.Profile.count_all(models.Profile)

        profiles = db.GqlQuery("SELECT * FROM Profile ORDER BY registered DESC")#models.Profile.all()
        self.generate('profileHome.html', {'profiles':profiles,'totalusercount':totalusers,
            'totalcomments':totalcomments})

class LeagueAll(web.BaseRequestHandler):
    def get(self):
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

class LeagueBySport(web.BaseRequestHandler):
    def get(self):
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

class TeamAll(web.BaseRequestHandler):
    def get(self):
        league = None
        sport = None
        #teams = models.Team.byLeagueBySport(league, sport)
        teams = db.GqlQuery('SELECT * FROM Team ORDER BY name ASC')
        self.generate('teamHome.html', {'teams':teams})

class TeamByLeague(web.BaseRequestHandler):
    def get(self):
        teams = models.League.all()
        self.generate('teamHome.html', {'teams':teams})

class MatchAll(web.BaseRequestHandler):
    def get(self):
        matches = models.Match.all()
        matches = db.GqlQuery('SELECT * FROM Match ORDER BY sport, league, matchStart DESC')
        self.generate('matchHome.html', {'matches':matches})

class MatchByLeague(web.BaseRequestHandler):
    def get(self):
        matches = models.Match.all()
        self.generate('matchHome.html', {'matches':matches})

class Match(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        comments = models.Comment.byMatch(match)
        self.generate('match.html', {'match': match, 'comments':comments})

class MatchAdd(web.BaseRequestHandler):
    def get(self):
        name = self.request.get('name')
        sideA = self.request.get('sideA')
        sideB = self.request.get('sideB')
        scoreA = '1'#self.request.get('scoreA')
        scoreB = '0'#self.request.get('scoreB')
        match = models.Match(name=name, sideA=sideA, sideB=sideB, scoreA=scoreA, scoreB=scoreB)
        match.put()
        comments = models.Comment.byMatch(match)
        self.redirect('match?key=%s' % (match.key()))

class MatchNew(web.BaseRequestHandler):
    def get(self):
        self.generate('matchNew.html', {})

application = webapp.WSGIApplication(
    [('/adminSportAll', SportAll),
    ('/adminLeagueAll', LeagueAll),
    ('/adminLeagueBySport', LeagueBySport),
    ('/adminTeamAll', TeamAll),
    ('/adminTeamByLeague', TeamByLeague),
    ('/adminMatchAll', MatchAll),
    ('/adminProfileAll', ProfileAll),
    ('/adminMatchByLeague', MatchByLeague),
    ('/admin', Admin),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
