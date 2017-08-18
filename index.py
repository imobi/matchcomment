from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import models
import web
from google.appengine.ext import db
import datetime
import time
from django.core.paginator import ObjectPaginator, InvalidPage
from django.utils import simplejson
import urllib
import urllib2
import facebook
import os.path
import wsgiref.handlers
import base64
import Cookie
import email.utils
import hashlib
import hmac
import logging
import os.path
import rest
import re
from django.http import HttpResponseRedirect
import lib.minidetector
import cgi #for facebook login

#mobile browser detection
reg_b = re.compile(r"android|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I|re.M)

FACEBOOK_APP_ID = "202309806462135"
FACEBOOK_APP_SECRET = "fdb4ba4d830eeccd8d7412a46b3ad9ec"
FACEBOOK_APP_KEY = "d819530b00ae34834ed7171072897388"

class MainPage(web.BaseRequestHandler):
    def get(self):
        #Detect the browser type
        browserType = None
        browserType = lib.minidetector.Middleware.process_request(self.request.headers)

        now = datetime.datetime.now() #up and coming fixtures
        profile = web.getuserprofile(self)
        #data from queries below should be cached
        matches = db.GqlQuery("SELECT * FROM Match WHERE matchStart > :1 ORDER BY matchStart ASC", now).fetch(5)
        sports = db.GqlQuery("SELECT * FROM Sport ORDER BY type ASC") #sorted all sports
        leagues = None
        #teams = None
        sportselected = None #user preference
        league = None #user preference
        
        matchfilter = "now"

        matchFavourites = None
        if hasattr(profile, "matchFavourites"):
            matchFavourites = db.get(profile.matchFavourites)

        if hasattr(profile, "sportPreference"):
            if profile.sportPreference == None:
                sportselected = sports[0]
                leagues = models.League.bySport(sportselected) #show default leagues from top sport in list
            else:
                leagues = models.League.bySport(profile.sportPreference) #show leagues for sport preference
                sportselected = profile.sportPreference

                if hasattr(profile, "newsItemCount"):
                    newsItemCount = profile.newsItemCount

                if leagues.count() > 0:
                    if profile.leaguePreference == None:
                        matches = models.Match.bySportAfterNow(profile.sportPreference, now)
                        #matches = db.GqlQuery('SELECT * FROM Match WHERE matchStart > :1 AND sport = :2 ORDER BY matchStart ASC', now, sport).fetch(int(newsItemCount))
                    else:
                        league = profile.leaguePreference
                        matches = models.Match.byLeagueAfterNow(profile.leaguePreference, now)
        #paging comments begin
        #try:
        #    page = int(self.request.get('page')) - 1
        #except:
        #    page = 0
        comments = models.Comment.byTimeDecending(5)

        showsportlinks = 1 #track whether to show sport links on the page or not

        '''
        THIS FACEBOOK INTEGRATION CODE WORKS BEGIN
                #user = models.User.get(profile.facebookid) #facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
                #if user:
                graph = facebook.GraphAPI("202309806462135|f8fd801bc238d4d4a5f1e4b7.1-748530309|29ekIMOspaBY4ndyxU3iLqmgAK4")#(user.access_token)
                    #write to user wall
                statusmessage = {"name": "Link name",
                     "link": "http://www.example.com/",
                     "caption": "{*actor*} posted a new review",
                     "description": "This is a longer description of the attachment",
                     "picture": "http://www.example.com/thumbnail.jpg"}
                graph.put_wall_post("test message", statusmessage, "me")
        THIS FACEBOOK INTEGRATION CODE WORKS END
        '''

        self.generate('index.html', {
            'matches':matches,
            'sports':sports,
            'matchFavourites':matchFavourites,
            'leagues':leagues,
            'sportselected':sportselected,
            'league':league,
            'comments':comments,
            'profile':profile,
            'browserType': browserType,
            'showsportlinks': showsportlinks,
            'matchfilter': matchfilter
            })
    
    #memcache version
    def get_leagues(self):
        leagues = memcache.get("leagues")
        if leagues is not None:
            return leagues
        else:
            leagues = models.League.all()
            if not memcache.add("leagues", leagues, 86400): #store for 24 hours
                logging.error("Memcache set failed")
            return leagues


class AboutPage(web.BaseRequestHandler):
    def get(self):
        self.generate('index.html', {})

class RegistrationPage(web.BaseRequestHandler):
    def get(self):
        self.generate('register.html', {})

class LoginPageView(web.BaseRequestHandler):
    def get(self):
        self.generate('login.html', {})

    def post(self):
        """This will handle logging via the generic MatchComment Login"""
        
        userLogin = self.request.get('login_userlogin')
        password = self.request.get('login_password')
        
        user = models.Profile.findProfile(userLogin, password)
        if user:
                self._current_user = user
                self.generate('index.html', {})
        else:
            self.generate('login.html', {})

class FacebookLoginPage(web.BaseRequestHandler):
    @property
    def current_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._current_user = models.User.get_by_key_name(user_id)
        return self._current_user
    
    def get(self):
        self.generate('facebooklogin.html', {'user':self.current_user})

'''
{
   "id": "220439",
   "name": "Bret Taylor",
   "first_name": "Bret",
   "last_name": "Taylor",
   "link": "http://www.facebook.com/btaylor",
   "gender": "male",
   "locale": "en_US"
}
'''

class FacebookLogin(web.BaseRequestHandler):
    @property
    def current_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._current_user = models.User.get_by_key_name(user_id)
        return self._current_user

    #@login_required
    def get(self):
        #verification_code = self.request.get("code")
        redirecturl = self.request.path_url
        
        args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url)      
        
        #extended permissions allow user to post to facebook status...
        args["scope"] = "publish_stream,email,offline_access,read_stream"
        # args["perms"] = "email,offline_access" 
        
        if self.request.get("code"):

            args["client_secret"] = FACEBOOK_APP_SECRET
            args["code"] = self.request.get("code")       
            #modify to accept extended permissions for updating users facebook status
            response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]
            
            # Download the user profile and cache a local instance of the
            # basic profile info
            fbprofile = simplejson.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=access_token))))
            user = models.User(key_name=str(fbprofile["id"]), id=str(fbprofile["id"]),
                        name=fbprofile["name"], access_token=access_token,
                        profile_url=fbprofile["link"])
            user.put()
            #create the same profile if the profile does not exist in the database...
            #profile = models.Profile.load(str(fbprofile["id"]))
            fbuser = users.User(str(fbprofile["id"]))
            #profile = db.GqlQuery("SELECT * FROM Profile WHERE facebookid = :facebookid", facebookid = str(fbprofile["id"]))
            profile = models.Profile.loadfacebookuser(str(fbprofile["id"]))
            if not profile:
                profile = models.Profile(user=fbuser) #user with fb id
                profile.alias = fbprofile["name"] #set email as default alias
                profile.name = fbprofile["first_name"] #set email as default alias
                profile.surname = fbprofile["last_name"] #set email as default alias
                profile.gender = fbprofile["gender"] #set email as default alias
                profile.profilePicture = "/images/silhouette.png" #set email as default alias
                profile.facebookid = str(fbprofile["id"])
                profile.loginMechanism = "facebook"
                profile.userType = "user"
                profile.newsItemCount = "3"
                profile.email = fbprofile["email"]
                profile.put()

            set_cookie(self.response, "fb_user", str(fbprofile["id"]), expires=time.time() + 31104000)#1 year expire
            #remove existing login cookie
            set_cookie(self.response, "loggedinuser", "", expires=time.time() - 31104000)
            set_cookie(self.response, "loginmechanism", "", expires=time.time() - 31104000)

            #create new login cookie
            set_cookie(self.response, "loggedinuser", str(str(fbprofile["id"])), expires=time.time() + 31104000)
            set_cookie(self.response, "loginmechanism", "facebook", expires=time.time() + 31104000)
            #self.redirect("/")
            #self.redirect("/facebookLoginPage")
            self.generate('login.html', {'user':self.current_user, 'profile':profile })
            #self.redirect("/facebookLoginPage")
            #self.redirect("/")
        else:
            self.redirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))

class FacebookLogout(web.BaseRequestHandler):
    def get(self):
        set_cookie(self.response, "fb_user", "", expires=time.time() - 31104000)
        set_cookie(self.response, "loggedinuser", "", expires=time.time() - 31104000)
        set_cookie(self.response, "loginmechanism", "", expires=time.time() - 31104000)
        self.redirect("/")

################################################################################
############################## FACEBOOK DEFS BEGIN #############################
################################################################################

def set_cookie(response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain: cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))

def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None

def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()

################################################################################
############################## FACEBOOK DEFS END ###############################
################################################################################

#gmail login
class LoginFilter(web.BaseRequestHandler):
    #@login_required
    def get(self):
        cont = self.request.get('cont')
        if not cont:
            cont = '/'
        profile = models.Profile.load(users.get_current_user())
        #remove existing login cookie
        set_cookie(self.response, "loggedinuser", "", expires=time.time() - 31104000)
        set_cookie(self.response, "loginmechanism", "", expires=time.time() - 31104000)
        #create new login cookie
        set_cookie(self.response, "loggedinuser", str(users.get_current_user()), expires=time.time() + 31104000)
        set_cookie(self.response, "loginmechanism", "gmail", expires=time.time() + 31104000)
        if not profile:
            profile = models.Profile(user=users.get_current_user())
            profile.alias = users.get_current_user().nickname() #set email as default alias
            profile.profilePicture = "/images/silhouette.png" #set email as default alias
            profile.loginMechanism = "gmail"
            profile.userType = "user"
            profile.newsItemCount = "3"
            profile.email = users.get_current_user().email()
            profile.put()
        self.redirect(cont)

#gmail login
class LogoutFilter(web.BaseRequestHandler):
    def get(self):
        cont = self.request.get('cont')
        if not cont:
            cont = '/'
        #remove existing login cookie
        set_cookie(self.response, "loggedinuser", "", expires=time.time() - 31104000)
        set_cookie(self.response, "loginmechanism", "", expires=time.time() - 31104000)
        self.redirect(cont)

#janrain login
class JanrainLoginUser(web.BaseRequestHandler):
    def post(self):
        # Step 1) Extract the token from your environment.  If you are using app engine,
        # you'd do something like:
        token = self.request.get('token')
        # Step 2) Now that we have the token, we need to make the api call to auth_info.
        # auth_info expects an HTTP Post with the following paramters:
        api_params = {
            'token': token,
            'apiKey': '7826055dcb05fae95cc6ed612069084296abe074',
            'format': 'json',
        }
        # make the api call
        #http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params))
        # read the json response
        #auth_info_json = http_response.read()
        # Step 3) process the json response
        #auth_info = json.loads(auth_info_json)
        auth_info = simplejson.load(urllib.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params)))

        # Step 4) use the response to sign the user in
        if auth_info['stat'] == 'ok':
            profile = auth_info['profile']
            # 'identifier' will always be in the payload
            # this is the unique idenfifier that you use to sign the user
            # in to your site
            identifier = profile['identifier']
            # these fields MAY be in the profile, but are not guaranteed. it
            # depends on the provider and their implementation.
            name = profile.get('displayName')
            email = profile.get('email')
            profile_pic_url = profile.get('photo')
            # actually sign the user in.  this implementation depends highly on your
            # platform, and is up to you.
            #sign_in_user(identifier, name, email, profile_pic_url)
            self.generate('janrainresult.html', {
                'identifier':identifier,
                'name':name,
                'email':email,
                'profile_pic_url':profile_pic_url
            })
        else:
            print 'An error occured: ' + auth_info['err']['msg']
        #self.redirect(cont)

class TwitterLogin(web.BaseRequestHandler):
    def get(self):
        self.generate('loginTwitter.html', {})

#News page
class News(web.BaseRequestHandler):
    def get(self):
        self.generate('news.html', {})

#Sitemap
class SiteMap(web.BaseRequestHandler):
    def get(self):
        self.generate('sitemap.xml', {})

#Sitemap
class Robots(web.BaseRequestHandler):
    def get(self):
        self.generate('robots.txt', {})
        
#Widget Test
class WidgetTest(web.BaseRequestHandler):
    def get(self):
        self.generate('widget.html', {})

class DetectMobileBrowser(web.BaseRequestHandler):
    def process_request(self, request):
        request.mobile = False
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return HttpResponseRedirect("http://detectmobilebrowser.com/mobile")

class CatchAll(web.BaseRequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('index 404')

application = webapp.WSGIApplication(
    [('/', MainPage),
        ('/loginFilter', LoginFilter),
        ('/logoutFilter', LogoutFilter),
        ('/about', AboutPage),
        ('/register', RegistrationPage),
        ('/loginPageView', LoginPageView),
        ('/facebookLoginPage', FacebookLoginPage),
        ('/facebookLogin', FacebookLogin),
        ('/facebookLogout', FacebookLogout),
        ('/janrainloginuser', JanrainLoginUser),
        ('/twitterLogin', TwitterLogin),
        ('/news', News),
        ('/sitemap.xml', SiteMap),
        ('/robots.txt', Robots),
        ('/widget', WidgetTest),
        ('/.*', CatchAll),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()