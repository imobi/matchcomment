from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web

class Player(web.BaseRequestHandler):
    def get(self):
        players = models.Player.all()
        self.generate('playerHome.html', {'players':players})

#form to add a new player
class PlayerNew(web.BaseRequestHandler):
    def get(self):
        #sport = db.get(self.request.get('teamsportkey'))
        #league = db.get(self.request.get('teamleaguekey'))
        sports = models.Sport.all()
        leagues = models.League.all()
        teams = models.Teams.all()
        #self.generate('teamNew.html', {'sports':sports, 'teamsportkey':sport.key, 'leagues':leagues, 'teamleaguekey':league.key})
        self.generate('playerNew.html', {'sports':sports, 'leagues':leagues, 'teams':teams})

class PlayerAdd(web.BaseRequestHandler):
    def post(self):
        avatar = None
        if self.request.get("avatar"):
            avatar = db.Blob(self.request.get("avatar"))
        facebookid = self.request.get('facebookid')
        twitterid = self.request.get('twitterid')
        name = self.request.get('name')
        description = self.request.get('description')
        sportkey = self.request.get('sportkey')
        leaguekey = self.request.get('leaguekey')
        teamkey = self.request.get('teamkey')
        country = self.request.get('country')
        city = self.request.get('city')
        club = self.request.get('club')
        sport = db.get(sportkey)
        league = db.get(leaguekey)
        team = db.get(teamkey)
        profile = profile = web.getuserprofile(self)
        user = profile.user#users.get_current_user()
        player = models.Player(
            name=name,
            description=description,
            sport=sport,
            league=league,
            club=club,
            country=country,
            city=city,
            facebookid=facebookid,
            twitterid=twitterid,
            avatar=avatar,
            user=user
        )
        player.put()
        players = models.Player.all()
        self.generate('playerHome.html', {'players':players})

class PlayerEdit(web.BaseRequestHandler):
    def get(self):
        team = models.Player.get(self.request.get('key'))
        sports = models.Sport.all()
        leagues = models.League.all()
        teams = models.Team.all()
        self.generate('playerEdit.html', {'team':team, 'sports':sports, 'leagues':leagues, 'players':players})

class PlayerUpdate(web.BaseRequestHandler):
    def post(self):
        player = models.Player.get(self.request.get('key'))
        sport = db.get(self.request.get('sportkey'))
        league = db.get(self.request.get('leaguekey'))
        team = db.get(self.request.get('teamkey'))
        player.name = self.request.get('name')
        player.description = self.request.get('description')
        player.country = self.request.get('country')
        player.city = self.request.get('city')
        player.sport = sport;
        player.league = league;
        player.club = self.request.get('club')
        player.facebookid = self.request.get('facebookid')
        player.twitterid = self.request.get('twitterid')
        if self.request.get("avatar"):
            team.avatar = db.Blob(self.request.get("avatar"))
        #do a check if this user is authorised to update this team
        player.save()
        self.redirect('player?key=%s' % (player.key()))

class PlayerDelete(web.BaseRequestHandler):
    def get(self):
        player = models.Player.get(self.request.get('key'))
        player.delete()
        players = models.Player.all()
        self.generate('playerHome.html', {'players':players})

#the user can view a list of all players by sport
class PlayerListBySport(web.BaseRequestHandler):
    def post(self):
        name = self.request.get('name')
        description = self.request.get('description')
        sportkey = self.request.get('sportkey')
        country = self.request.get('country')
        city = self.request.get('city')
        sport = db.get(sportkey)
        profile = profile = web.getuserprofile(self)
        user = profile.user#users.get_current_user()
        player = models.Player(name=name, description=description, sport=sport, country=country, city=city, user=user)
        player.put()
        players = models.Player.all()
        self.generate('playerHome.html', {'players':players})

class PlayerProfileView(web.BaseRequestHandler):
    def get(self):
        player = models.Player.get(self.request.get('key'))
        self.generate('player.html', {'player':player})

class Image (webapp.RequestHandler):
    def get(self):
      player = db.get(self.request.get("player"))
      if team.avatar:
          self.response.headers['Content-Type'] = "image/png"
          self.response.out.write(player.avatar)
      else:
          self.error(404)

application = webapp.WSGIApplication(
    [('/player', Player),
        ('/playerAdd', PlayerAdd),
        ('/playerNew', PlayerNew),
        ('/playerEdit', PlayerEdit),
        ('/playerDelete', PlayerDelete),
        ('/playerUpdate', PlayerUpdate),
        ('/playerProfileView', PlayerProfileView),
        ('/playerimg', Image),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()