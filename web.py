from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import models
import os
import logging

webapp.template.register_template_library('templatetags.templatefilters')
webapp.template.register_template_library('templatetags.iftag')
webapp.template.register_template_library('templatetags.userprofilefilters')
webapp.template.register_template_library('templatetags.datetimefilters')
webapp.template.register_template_library('templatetags.variablestag')

import time
import base64
import Cookie
import hmac
import hashlib
import email.utils
import datetime

FACEBOOK_APP_ID = "202309806462135"
FACEBOOK_APP_SECRET = "fdb4ba4d830eeccd8d7412a46b3ad9ec"
FACEBOOK_APP_KEY = "d819530b00ae34834ed7171072897388"

def getuserprofile(self):
    loggedinuser = parse_cookie(self.request.cookies.get("loggedinuser"))
    loginmechanism = parse_cookie(self.request.cookies.get("loginmechanism"))
    profile = None
    if loggedinuser:
        if loginmechanism == "gmail":
            profile = models.Profile.load(users.get_current_user())
        elif loginmechanism == "facebook":
            profile = models.Profile.loadfacebookuser(str(loggedinuser))
    return profile

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

class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  def generate(self, template_name, template_values={}):
    #loggedinuser = parse_cookie(self.request.cookies.get("loggedinuser"))
    #loginmechanism = parse_cookie(self.request.cookies.get("loginmechanism"))
    profile = getuserprofile(self)
    loggedinuser = None
    loginmechanism = None
    if profile:
        loggedinuser = profile.user
        loginmechanism = profile.loginMechanism
    #user = users.get_current_user()
    user = loggedinuser

    values = {
      'request': self.request,
      'user': user,
      'loggedinuser': loggedinuser,
      'loginmechanism': loginmechanism,
      'profile': profile,
      'admin': users.is_current_user_admin(),
      'login_url': users.create_login_url('/loginFilter?cont='+self.request.uri),
      'logout_url': users.create_logout_url('/logoutFilter?cont='+self.request.uri),
    }
    values.update(template_values)
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', template_name))
    self.response.out.write(template.render(path, values))

  def head(self, *args):
        pass

  def get(self, *args):
        pass

  def post(self, *args):
        pass