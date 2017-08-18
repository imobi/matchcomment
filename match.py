from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web
import datetime
import time
from django.core.paginator import ObjectPaginator, InvalidPage
import lib.minidetector

class Match(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        user = users.get_current_user()
        profile = web.getuserprofile(self)

        #add to the users match favourite / 'check the user in' to the match
        if profile:
            try:
                profile.matchFavourites.index(match.key())
            except ValueError:
                profile.matchFavourites.append(match.key())
                profile.put()
                #generate check in comment for user to publish to main matchcomment timeline
                commenttype = 'checkin'
                useralias = profile.alias
                text = "checkin"
                comment = models.Comment(
                    text=text,
                    user=profile.user,
                    match=match,
                    useralias=useralias,
                    commenttype=commenttype,
                    profile=profile
                )
                comment.put()
                #post message to facebook, twitter, bbm that user has checked into a match
                #so that other users can join the match comment chat
                #socialnetworks.post("Joe checked into Arsenal vs Manchester United via mobile on MatchComment")

        #paging comments begin
        try:
            page = int(self.request.get('page')) - 1
        except:
            page = 0
        comments = models.Comment.byMatch(match)
        paginator = ObjectPaginator(comments, 10)
        if page >= paginator.pages:
            page = paginator.pages - 1
        #paging comments end

        teamSupportedInMatch = models.TeamSupportedInMatch.getTeamForMatch(profile, match)

        self.generate('match.html', {
            'match':match,
            'profile':profile,
            'comments':paginator.get_page(page),
            'pages':range(1, paginator.pages + 1),
            'page':page + 1,
            'teamSupportedInMatch': teamSupportedInMatch
        })

class MatchNew(web.BaseRequestHandler):
    def get(self):
        league = db.get(self.request.get('matchleaguekey'))
        leagues = models.League.bySport(league.sport)
        teams = db.GqlQuery('SELECT * FROM Team WHERE league = :league ORDER BY name ASC', league=league)
        matchStart = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.generate('matchNew.html', {'leagues':leagues, 'teams':teams, 'matchleaguekey':league.key, 'matchStart': matchStart, 'sport':league.sport})

class MatchAdd(web.BaseRequestHandler):
    def get(self):
        league = db.get(self.request.get('leaguekey'))
        sport = models.Sport.get(self.request.get('sportkey'))
        hometeam = db.get(self.request.get('hometeamkey'))
        awayteam = db.get(self.request.get('awayteamkey'))
        name = hometeam.name + " vs " + awayteam.name #self.request.get('name')
        sideA = hometeam
        sideB = awayteam
        scoreA = '0'#self.request.get('scoreA')
        scoreB = '0'#self.request.get('scoreB')
        matchStart = datetime.datetime.strptime(self.request.get('matchStart'), '%Y-%m-%d %H:%M')
        profile = web.getuserprofile(self)
        user = profile.user
        matchPeriod = '1st Half'
        match = models.Match(name=name, sideA=sideA, sideB=sideB, scoreA=scoreA, scoreB=scoreB, league=league, sport=sport, matchStart=matchStart, matchPeriod=matchPeriod, user=user)
        match.put()
        leagues = models.League.all()
        self.generate('leagueHome.html', {'leagues':leagues})

class MatchEdit(web.BaseRequestHandler):
    def get(self):        
        match = models.Match.get(self.request.get('key'))
        matchhometeam = match.sideA
        matchawayteam = match.sideB
        league = models.League.get(self.request.get('leaguekey'))
        leagues = models.League.all()
        teams = db.GqlQuery('SELECT * FROM Team WHERE league = :league ORDER BY name ASC', league=league)
        self.generate('matchEdit.html', {
            'match':match,
            'leagues':leagues,
            'teams':teams,
            'matchhometeam':matchhometeam,
            'matchawayteam':matchawayteam
            })

class MatchUpdate(web.BaseRequestHandler):
    def post(self):
        match = models.Match.get(self.request.get('key'))
        match.league = db.get(self.request.get('leaguekey'))
        match.sport = match.league.sport
        hometeam = db.get(self.request.get('hometeamkey'))
        awayteam = db.get(self.request.get('awayteamkey'))
        match.name = hometeam.name + " vs " + awayteam.name #self.request.get('name')
        match.sideA = hometeam
        match.sideB = awayteam
        timestring = self.request.get("matchStart")
        time_format = "%Y-%m-%d %H:%M:%S"
        match.matchStart = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timestring, time_format)))
        #do a check if this user is authorised to update this match
        match.save()
        self.redirect('matchEdit?key=%s' % (match.key()) + '&leaguekey=' + self.request.get('leaguekey'))

class MatchDelete(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        match.delete()
        self.generate('matchHome.html', {})

class MatchScoreUpdate(web.BaseRequestHandler):
    def post(self):
        match = models.Match.get(self.request.get('key'))
        match.scoreA = self.request.get('scoreA')
        match.scoreB = self.request.get('scoreB')
        match.matchPeriod = self.request.get('matchPeriod')
        match.save()
        #self.redirect('match?key=%s' % (match.key()))
        self.redirect(self.request.get('redirect'))

class MatchUpdateSupporters(web.BaseRequestHandler):
    def post(self):
        match = models.Match.get(self.request.get('key'))
        match.scoreA = self.request.get('scoreA')
        match.scoreB = self.request.get('scoreB')
        match.matchPeriod = self.request.get('matchPeriod')
        match.save()
        #self.redirect('match?key=%s' % (match.key()))
        self.redirect(self.request.get('redirect'))

class MatchSearch(web.BaseRequestHandler):
    def post(self):
        matches = None
        fromsearch = self.request.get('fromsearch')
        sportsearchkeyselected = self.request.get('sportsearchkey')
        leaguesearchkeyselected = self.request.get('leaguesearchkey')
        #teamsearchkeyselected = self.request.get('teamsearchkey')
        #sport = None
        #if sportsearchkeyselected  != "All":
        sport = models.Sport.get(sportsearchkeyselected)
        leagues = models.League.bySport(sport)
        league = None
        if leaguesearchkeyselected != "All":
            league = models.League.get(leaguesearchkeyselected)
            matches = models.Match.byLeagueAfterNow(league, datetime.datetime.now())
        else: 
            matches = models.Match.bySportAfterNow(sport, datetime.datetime.now())
        #teams = models.Team.byLeague(league)
        #team = None
        #if teamsearchkeyselected  != "":
        #    team = models.Team.get(teamsearchkeyselected)
        #    matches = models.Match.byLeagueByTeam(league, team)
        
        #matches = db.GqlQuery("SELECT * FROM Match ORDER BY matchStart ASC")
        user = users.get_current_user()
        profile = web.getuserprofile(self)#models.Profile.load(user)
        matchFavourites = None
        if hasattr(profile, "matchFavourites"):
            matchFavourites = db.get(profile.matchFavourites)

        sports = db.GqlQuery("SELECT * FROM Sport ORDER BY type ASC") #sorted sports

        comments = models.Comment.byLeague(leagueselected, 5)

        self.generate('index.html', {
            'matches':matches,
            'sports':sports,
            'sport':sport,
            'league':league,
            'matchFavourites':matchFavourites,
            'fromsearch':fromsearch,
            'leagues':leagues,
            'comments':comments,
            'sportsearchkeyselected':sportsearchkeyselected,
            'leaguesearchkeyselected':leaguesearchkeyselected
        })

#the user can view a list of all matches by league
class MatchListByLeague(web.BaseRequestHandler):
    def get(self):
        '''league = models.League.get(self.request.get('key'))
        matches = db.GqlQuery('SELECT * FROM Match WHERE league = :league ORDER BY matchStart DESC', league=league)
        self.generate('matchListByLeague.html', {'matches':matches, 'league':league})
'''
        #Detect the browser type
        browserType = None
        browserType = lib.minidetector.Middleware.process_request(self.request.headers)
        now = datetime.datetime.now() #up and coming fixtures
        profile = web.getuserprofile(self)

        sports = models.Sport.all()
        leagues = None

        matchFavourites = None
        if hasattr(profile, "matchFavourites"):
            matchFavourites = db.get(profile.matchFavourites)

        sportselected = models.Sport.get(self.request.get('sportkey'))
        leagueselected = None

        leagues = db.GqlQuery('SELECT * FROM League WHERE sport = :1 ORDER BY name ASC', sportselected)

        if self.request.get('key'):
            leagueselected = models.League.get(self.request.get('key'))
        else:
            leagueselected = leagues[0]

        if leagues.count() > 0:
            league = leagueselected

        matches = None
        matchfilter = ""
        if self.request.get('matchfilter'): #flag to determine whether to show latest or all matches
            matches = models.Match.byLeague(leagueselected)
            matchfilter = "all"
        else: #show only up and coming matches
            matches = models.Match.byLeagueAfterNow(leagueselected, now)
            matchfilter = "now"

        comments = models.Comment.byLeague(leagueselected, 5)
        showsportlinks = 0  #track whether to show sport links on the page or not

        self.generate('matchListByLeague.html', {
            'matches':matches,
            'sports':sports,
            'matchFavourites':matchFavourites,
            'leagues':leagues,
            'league':league,
            'comments':comments,
            'profile':profile,
            'browserType': browserType,
            'sportselected':sportselected,
            'leagueselected':leagueselected,
            'showsportlinks': showsportlinks,
            'matchfilter': matchfilter
            })

application = webapp.WSGIApplication(
    [('/match', Match),
        ('/matchAdd', MatchAdd),
        ('/matchNew', MatchNew),
        ('/matchEdit', MatchEdit),
        ('/matchDelete', MatchDelete),
        ('/matchUpdate', MatchUpdate),
        ('/matchScoreUpdate', MatchScoreUpdate),
        ('/matchSearch', MatchSearch),
        ('/matchListByLeague', MatchListByLeague),
        ('/matchUpdateSupporters', MatchUpdateSupporters),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()