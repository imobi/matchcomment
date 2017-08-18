import comment
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import models
import web
from google.appengine.api import mail
#from google.appengine.api import images

class Profile(web.BaseRequestHandler):
    #@login_required
    def get(self):
        user = users.get_current_user() #adjust for facebook login
        profile = web.getuserprofile(self)#models.Profile.load(user)
        matchFavourites = None
        if hasattr(profile, "matchFavourites"):
            matchFavourites = db.get(profile.matchFavourites)
        sports = db.GqlQuery("SELECT * FROM Sport ORDER BY type ASC") #sorted sports
        leagues = None
        if hasattr(profile, "sportPreference"):
            leagues = models.League.bySport(profile.sportPreference)
        else:
            leagues = models.League.bySport(sports[0])
        self.generate('profile.html', {'profile':profile, 'matchFavourites':matchFavourites, 'sports':sports, 'leagues':leagues})

class ProfileEdit(web.BaseRequestHandler):
    def get(self):
        profile = models.Profile.get(self.request.get('key'))
        self.generate('profileEdit.html', {'profile':profile})

class ProfileAdminUpdate(web.BaseRequestHandler):
    def post(self):
        profile = models.Profile.get(self.request.get('key'))
        profile.alias = self.request.get('alias')
        profile.loginMechanism = self.request.get('loginMechanism')
        profile.userType = self.request.get('userType')
        profile.save()

        #testing email sending begin...
        #message = mail.EmailMessage(sender="MatchComment.com Support <admin@matchcomment.com>",
        #                            subject="Your MatchComment account has been upgraded")
        #message.to = profile.email
        #message.body = """ %s, your MatchComment account has been upgraded via www.matchcomment.com """ % profile.name
        #message.send()
        #testing email sending end...

        self.redirect(self.request.get('redirect'))

class ProfileDelete(web.BaseRequestHandler):
    def get(self):
        #profile = models.Profile.get(self.request.get('key'))
        #profile.delete()
        #profiles = models.Profile.all()
        self.generate('profileHome.html', {'profiles':profiles})

class ProfileUpdate(web.BaseRequestHandler):
    def post(self):
        profile = models.Profile.get(self.request.get('key'))
        profile.alias = self.request.get('alias')
        profile.name = self.request.get('name')
        profile.surname = self.request.get('surname')
        profile.email = self.request.get('email')
        profile.mobile = self.request.get('mobile')
        profile.city = self.request.get('city')
        profile.country = self.request.get('country')
        profile.gender = self.request.get('gender')
        profile.sportPreference = models.Sport.get(self.request.get('sportPreference'))
        profile.newsItemCount = self.request.get('newsItemCount')
        if self.request.get('leaguePreference') != 'None':
            profile.leaguePreference = models.League.get(self.request.get('leaguePreference'))
        else:
            profile.leaguePreference = None
        profile.loginMechanism = self.request.get('loginMechanism')
        profile.profilePicture = self.request.get('profilePicture')
        if self.request.get("avatar"):
            profile.avatar = db.Blob(self.request.get("avatar"))
        profile.save()
        self.redirect(self.request.get('redirect'))

class CatchAll(web.BaseRequestHandler):
    def get(self):
        #try to resolve the text of the profile
        
        
        self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write('profile 404')
        self.response.out.write(self.request.path) #extract the path and resolve the user profile

class ProfileMatchAdd(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.matchFavourites.append(match.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileTeamAdd(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.teams.append(team.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileAddFollower(web.BaseRequestHandler):
    def get(self):
        fan = models.Profile.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.followers.append(fan.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileLeagueAdd(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.leagueFavourites.append(match.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileMatchDelete(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.matchFavourites.remove(match.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileTeamDelete(web.BaseRequestHandler):
    def get(self):
        team = models.Team.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.teams.remove(team.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileRemoveFollower(web.BaseRequestHandler):
    def get(self):
        fan = models.Profile.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.followers.remove(fan.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileLeagueDelete(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        profile.leagueFavourites.remove(match.key())
        profile.put()
        redirect = self.request.get('redirect')
        self.redirect(redirect)
        
class ProfileTeamSupportForMatch (web.BaseRequestHandler):
    def get(self):
        profile = web.getuserprofile(self)
        match = models.Match.get(self.request.get('match'))
        #remove existing team supported in match for user
        list = db.GqlQuery('SELECT * FROM TeamSupportedInMatch WHERE profile = :profile AND match = :match', profile=profile, match=match)
        for entity in list:
          db.delete(entity)

        teamKey = self.request.get('team')
        if teamKey != "":
            team = models.Team.get(teamKey) #this will be sideA or sideB from where we can find the match
            #add team that the user supports for this match
            teamSupportedInMatch = models.TeamSupportedInMatch(match=match, team=team, profile=profile)
            teamSupportedInMatch.put()
            #generate team supported comment for user to publish to main matchcomment timeline
            commenttype = 'teamsupport'
            useralias = profile.alias
            text = teamKey
            comment = models.Comment(
                text=text,
                user=profile.user,
                match=match,
                useralias=useralias,
                commenttype=commenttype,
                profile=profile
            )
            comment.put()
            #post message to facebook, twitter, bbm that user has supported a specific team in a match
            #so that other users can join the match comment chat
            #socialnetworks.post("Joe supports Arsenal in Arsenal vs Manchester United via mobile on MatchComment")

        redirect = self.request.get('redirect')
        self.redirect(redirect)

class ProfileView(web.BaseRequestHandler):
    def get(self):
        comments = None
        matchFavourites = None
        teams = None
        followers = None
        profile = None
        if self.request.get('fromprofile'):
            user = users.get_current_user()
            profile = web.getuserprofile(self)#models.Profile.load(user)#user db.get like in matches
            if hasattr(profile, "matchFavourites"):
                matchFavourites = db.get(profile.matchFavourites)
                teams = db.get(profile.teams)
                followers = db.get(profile.followers)
                comments = models.Comment.byUser(models.Profile.load(user))
        else:
            #get user from comment key
            #comment = models.Comment.get(self.request.get('key'))
            #profile = models.Profile.load(comment.user)
            profile = models.Profile.get(self.request.get('key'))
            matchFavourites = db.get(profile.matchFavourites)
            teams = db.get(profile.teams)
            followers = db.get(profile.followers)
            comments = models.Comment.byUser(profile.user)

        showprofile = "true"
        self.generate('profile.html', {'profile':profile, 'showprofile':showprofile, 'matchFavourites':matchFavourites, 'teams':teams, 'followers':followers, 'comments':comments})

class Image(webapp.RequestHandler):
    def get(self):
      profile = db.get(self.request.get("profile"))
      if profile.avatar:
          self.response.headers['Content-Type'] = "image/png"
          self.response.out.write(profile.avatar)
      else:
          self.error(404)

application = webapp.WSGIApplication(
    [('/profile', Profile),
        ('/profileEdit', ProfileEdit),
        ('/profileAdminUpdate', ProfileAdminUpdate),
        ('/profileDelete', ProfileDelete),
        ('/profileUpdate', ProfileUpdate),
        ('/profileMatchAdd', ProfileMatchAdd),
        ('/profileLeagueAdd', ProfileLeagueAdd),
        ('/profileTeamAdd', ProfileTeamAdd),
        ('/profileFanAdd', ProfileAddFollower),
        ('/profileMatchDelete', ProfileMatchDelete),
        ('/profileLeagueDelete', ProfileLeagueDelete),
        ('/profileTeamDelete', ProfileTeamDelete),
        ('/profileFanDelete', ProfileRemoveFollower),
        ('/profileView', ProfileView),
        ('/profileimg', Image),
        ('/profileTeamSupportForMatch', ProfileTeamSupportForMatch),
        ('/.*', CatchAll),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()