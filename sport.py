from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web

class Sport(web.BaseRequestHandler):
    def get(self):
        sports = models.Sport.all()
        self.generate('sportHome.html', {'sports':sports})

class SportAdd(web.BaseRequestHandler):
    def post(self):
        type = self.request.get('type')
        description = self.request.get('description')
        sport = models.Sport(type=type, description=description)
        sport.put()
        sports = models.Sport.all()
        self.generate('sportHome.html', {'sports':sports})

class SportUpdate(web.BaseRequestHandler):
    def post(self):
        sport = models.Sport.get(self.request.get('key'))
        sport.type = self.request.get('type')
        sport.description = self.request.get('description')
        sport.save()
        self.redirect('sport?key=%s' % (sport.key()))

class SportDelete(web.BaseRequestHandler):
    def get(self):
        sport = models.Sport.get(self.request.get('key'))
        sport.delete()
        sports = models.Sport.all()
        self.generate('sportHome.html', {'sports':sports})

#form to add a new sport
class SportNew(web.BaseRequestHandler):
    def get(self):
        self.generate('sportNew.html', {})

class SportEdit(web.BaseRequestHandler):
    def get(self):
        sport = models.Sport.get(self.request.get('key'))
        self.generate('sportEdit.html', {'sport':sport})

#the user can view a list of all leagues by sport
class SportList(web.BaseRequestHandler):
    def get(self):
        sports = models.Sport.all()
        self.generate('sportList.html', {'sports':sports})

#show a form for a user to request a new sport
class SportRequest(web.BaseRequestHandler):
    def get(self):
        profile = web.getuserprofile(self)
        self.generate('sportRequest.html', {'profile': profile})

#process the user request to add a new sport
class SportRequestProcess(web.BaseRequestHandler):
    def get(self):
        sport = self.request.get('sport')
        name = self.request.get('name')
        surname = self.request.get('surname')
        email = self.request.get('email')
        country = self.request.get('country')
        city = self.request.get('city')

        #testing email sending begin...
        #message = mail.EmailMessage(sender="MatchComment.com Support <admin@matchcomment.com>",
        #subject = "A request for a new sport "
        #message.to = email
        #message.body = """ %s, your MatchComment account has been upgraded via www.matchcomment.com """ % profile.name
        #message.send()
        #testing email sending end...
        self.generate('sportRequest.html', {})

application = webapp.WSGIApplication(
    [('/sport', Sport),
        ('/sportAdd', SportAdd),
        ('/sportNew', SportNew),
        ('/sportEdit', SportEdit),
        ('/sportDelete', SportDelete),
        ('/sportUpdate', SportUpdate),
        ('/sportList', SportList),
        ('/sportRequest', SportRequest),
        ('/sportRequestProcess', SportRequestProcess),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()