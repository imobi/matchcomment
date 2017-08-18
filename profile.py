import models
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web

class Profile(web.BaseRequestHandler):
    @login_required
    def get(self):
        models.Profile.load(user)
        self.generate('profile.html', {})

class ProfileUpdate(web.BaseRequestHandler):
    def get(self):
        self.redirect('index.html')

class ProfileMatchAdd(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('matchKey'))
        redirect = self.request.get('redirect')
        self.response.redirect(redirect)

class ProfileFanAdd(web.BaseRequestHandler):
    def get(self):
        profile = models.Profile.get(self.request.get('key'))
        redirect = self.request.get('redirect')
        self.response.redirect(redirect)

class ProfileTeamAdd(web.BaseRequestHandler):
    def get(self):
        match = models.Match.get(self.request.get('key'))
        redirect = self.request.get('redirect')
        self.response.redirect(redirect)

class CatchAll(web.BaseRequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('profile 404')

application = webapp.WSGIApplication(
    [('/profile', Profile),
        ('/profileUpdate', ProfileUpdate),
        ('/profileMatchAdd', ProfileMatchAdd),
        ('/profileTeamAdd', ProfileTeamAdd),
        ('/profileFanAdd', ProfileFanAdd),
        ('/profileView', ProfileView),
        ('/.*', CatchAll),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()