from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web
from lib.twitter import twitter
import re
import random

class Team(web.BaseRequestHandler):
    def get(self):
        teams = models.Team.all()
        self.generate('teamHome.html', {'teams':teams})

#form to add a new team
class TeamNew(web.BaseRequestHandler):
    def get(self):
        #sport = db.get(self.request.get('teamsportkey'))
        #league = db.get(self.request.get('teamleaguekey'))
        sports = models.Sport.all()
        leagues = models.League.all()
        #self.generate('teamNew.html', {'sports':sports, 'teamsportkey':sport.key, 'leagues':leagues, 'teamleaguekey':league.key})
        self.generate('teamNew.html', {'sports':sports, 'leagues':leagues})

class TeamAdd(web.BaseRequestHandler):
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
        country = self.request.get('country')
        city = self.request.get('city')
        club = self.request.get('club')
        sport = db.get(sportkey)
        league = db.get(leaguekey)
        profile = web.getuserprofile(self)
        user = profile.user#users.get_current_user()
        team = models.Team(
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
        team.put()
        teams = models.Team.all()
        self.generate('teamHome.html', {'teams':teams})

class TeamEdit(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        sports = models.Sport.all()
        leagues = models.League.all()
        self.generate('teamEdit.html', {'team':team, 'sports':sports, 'leagues':leagues})

class TeamUpdate(web.BaseRequestHandler):
    def post(self):
        team = models.Team.get(self.request.get('key'))
        sport = db.get(self.request.get('sportkey'))
        league = db.get(self.request.get('leaguekey'))
        team.name = self.request.get('name')
        team.description = self.request.get('description')
        team.country = self.request.get('country')
        team.city = self.request.get('city')
        team.sport = sport
        team.league = league
        team.club = self.request.get('club')
        team.facebookid = self.request.get('facebookid')
        team.twitterid = self.request.get('twitterid')
        if self.request.get("avatar"):
            team.avatar = db.Blob(self.request.get("avatar"))
        #do a check if this user is authorised to update this team
        team.save()
        self.redirect('team?key=%s' % (team.key()))

class TeamDelete(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        team.delete()
        teams = models.Team.all()
        self.generate('teamHome.html', {'teams':teams})

#the user can view a list of all teams by sport
class TeamListBySport(web.BaseRequestHandler):
    def post(self):
        name = self.request.get('name')
        description = self.request.get('description')
        sportkey = self.request.get('sportkey')
        country = self.request.get('country')
        city = self.request.get('city')
        sport = db.get(sportkey)
        profile = web.getuserprofile(self)
        user = profile.user#users.get_current_user()
        team = models.Team(name=name, description=description, sport=sport, country=country, city=city, user=user)
        team.put()
        teams = models.Team.all()
        self.generate('teamHome.html', {'teams':teams})

class TeamProfileView(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        messages = []
        if team.twitterid != "":
            #get team tweets code below works
            user = team.twitterid
            messages_to_display = 5
            #api = twitter.Api() #this uses the public api limiting request to 150 per hour
            #changed to use matchcomment twitter user settings or authenticated users twitter settings
            #below is the parameters for the matchcomment twitter app, users will need separate oauth for posting to their twitter accounts
            api = twitter.Api(
                consumer_key='SYyUZrB1ZBnWmnNVDcTYqA',
                consumer_secret='BQLgC5o7ghHYWMKClJMwRxbRDiWEji3qqsL6OXzOc',
                access_token_key='15633711-hbqnvVrFecznVzBtCVndJDxoH1fhWFxgG153KPqfh',
                access_token_secret='H65F0WQ2o5OANG5jS1aBJodcMbcW5SP5rNAmLpvM'
            )
            #testing posting of comments to twitter adjust for user account in match comment section
            #works but gives TwitterError: Status is a duplicate.
            #api.PostUpdate('I love python-twitter via matchcomment.com ' + str(random.randint(0, 1000)))
            statuses = api.GetUserTimeline(screen_name=user, count=messages_to_display, include_entities=True)
            for status in statuses:
                # Replaces the @username mentions with a URL
                replaced_mentions = re.sub(r'(@[^ $]+)', r'<a target="_blank" href="http://twitter.com/\1">\1</a>',status.text);
                # Replaces the #tag's with a URL
                replaced_hashtags = re.sub(r'(#[^ $]+)', r'<a target="_blank" href="http://twitter.com/#!/search?q=%23\1">\1</a>',replaced_mentions);
                # Replaces the published times with a URL
                replaced_times = (replaced_hashtags + " "+
                                  "<span class='tiny-font'><a target='_blank' href='http://twitter.com/#!/"+
                                  user+"/status/"+str(status.id)+"'>"+str(status.relative_created_at+
                                  "</a></span>"))
                messages.append(replaced_times)
        else:
            messages.append("No twitter account available for " + team.name)
        self.generate('team.html', {'team':team, 'messages': messages})

class Image (webapp.RequestHandler):
    def get(self):
      team = db.get(self.request.get("team"))
      if team.avatar:
          self.response.headers['Content-Type'] = "image/png"
          self.response.out.write(team.avatar)
      else:
          self.error(404)

application = webapp.WSGIApplication(
    [('/team', Team),
        ('/teamAdd', TeamAdd),
        ('/teamNew', TeamNew),
        ('/teamEdit', TeamEdit),
        ('/teamDelete', TeamDelete),
        ('/teamUpdate', TeamUpdate),
        ('/teamProfileView', TeamProfileView),
        ('/teamimg', Image),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()