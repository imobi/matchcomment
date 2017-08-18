from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app
import models
import web
import twitter
import facebook

# FACEBOOK_APP_ID = "202309806462135"
FACEBOOK_APP_ID = "190486634333354"

FACEBOOK_APP_KEY = "4bbd0fbf47bd3bebefaf7339a682e83e"
# FACEBOOK_APP_SECRET = "fdb4ba4d830eeccd8d7412a46b3ad9ec"
FACEBOOK_APP_SECRET = "ff4e2800e5b930a5b488ed018fb66769"

class Add(web.BaseRequestHandler):
    def post(self):
        text = self.request.get('comment')
        if len(text) == 0:
            self.redirect(self.request.get('redirect'))
        else:
            match = models.Match.get(self.request.get('matchKey'))
            useralias = self.request.get('useralias')
            commenttype = '' #check the comment type for sorting
            if text.find('@h') != -1:
                commenttype = '@h'
            elif text.find('@a') != -1:
                commenttype = '@a'
            elif text.find('@r') != -1:
                commenttype = '@r'
            else:
                commenttype = 'comment'
            profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
            useralias = profile.alias
            comment = models.Comment(
                text=text,
                user=profile.user,
                match=match,
                league=match.league,
                sport=match.sport,
                useralias=useralias,
                commenttype=commenttype,
                profile=profile
            )
            comment.put()
            #post comment to twitter if username and password is enabled
            '''
            api = twitter.Api(
                consumer_key='SYyUZrB1ZBnWmnNVDcTYqA',
                consumer_secret='BQLgC5o7ghHYWMKClJMwRxbRDiWEji3qqsL6OXzOc',
                access_token_key='15633711-hbqnvVrFecznVzBtCVndJDxoH1fhWFxgG153KPqfh',
                access_token_secret='H65F0WQ2o5OANG5jS1aBJodcMbcW5SP5rNAmLpvM'
            )
            '''
            
            # status = api.PostUpdate('I love python-twitter!')
            
            #post comment to facebook  
            ''' For some Reason the cookies are not parsed
            
            cookie = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)  
            
            if cookie:
                 graph = facebook.GraphAPI(cookie["access_token"])
                 graph.put_object("me", "feed", message="Hello, world")
                 graph.put_wall_post("text")
                '''





            

            self.redirect(self.request.get('redirect'))

class CommentDelete(web.BaseRequestHandler):
    def get(self):
        comment = models.Comment.get(self.request.get('commentkey'))
        comment.delete()
        self.redirect(self.request.get('redirect'))

class CommentLike(web.BaseRequestHandler):
    def get(self):
        comment = models.Comment.get(self.request.get('commentkey'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        comment.likes.append(profile.key())
        comment.put()
        self.redirect(self.request.get('redirect'))

class CommentUnLike(web.BaseRequestHandler):
    def get(self):
        comment = models.Comment.get(self.request.get('commentkey'))
        profile = web.getuserprofile(self)#models.Profile.load(users.get_current_user())
        comment.likes.remove(profile.key())
        comment.put()
        self.redirect(self.request.get('redirect'))

class CommentLikeView(web.BaseRequestHandler):
    def get(self):
        comment = models.Comment.get(self.request.get('commentkey'))
        self.generate('commentLikeView.html', {'comment':comment})

class CommentRssFeed(web.BaseRequestHandler):
    def get(self):
        self.redirect(self.request.get('redirect'))
'''
class BuzzCommentsParser() Fan, Team, Player Buzz comments
    def get_facebook_comments(url, limit=3):
    
class FacebookCommentsParser() Fan, Team, Player Facebook comments
    def get_facebook_comments(url, limit=3):

class TwitterCommentsParser() Fan, Team, Player Twitter comments
def get_twitter(url, limit=3):
    """Takes a twitter rss feed and returns a list of dictionaries, one per
    tweet. Each dictionary contains two attributes:
        - An html ready string with the @, # and links parsed to the correct
        html code
        - A datetime object of the posted date"""

    twitter_entries = []
    for entry in feedparser.parse(url)['entries'][:limit]:

        # convert the given time format to datetime
        posted_datetime = datetime.datetime(
            entry['updated_parsed'][0],
            entry['updated_parsed'][1],
            entry['updated_parsed'][2],
            entry['updated_parsed'][3],
            entry['updated_parsed'][4],
            entry['updated_parsed'][5],
            entry['updated_parsed'][6],
        )

        # format the date a bit
        if posted_datetime.year == datetime.datetime.now().year:
            posted = posted_datetime.strftime("%b %d")
        else:
            posted = posted_datetime.strftime("%b %d %y")

        # strip the "<username>: " that preceeds all twitter feed entries
        text = re.sub(r'^\w+:\s', '', entry['title'])

# parse links
        text = re.sub(
            r"(http(s)?://[\w./?=%&\-]+)",
            lambda x: "<a href='%s'>%s</a>" % (x.group(), x.group()),
            text)

        # parse @tweeter
        text = re.sub(
            r'@(\w+)',
            lambda x: "<a href='http://twitter.com/%s'>%s</a>"\
                 % (x.group()[1:], x.group()),
            text)

        # parse #hashtag
        text = re.sub(
            r'#(\w+)',
            lambda x: "<a href='http://twitter.com/search?q=%%23%s'>%s</a>"\
                 % (x.group()[1:], x.group()),
            text)

        twitter_entries.append({
            'text': text,
            'posted': posted,
            })

    return twitter_entries
'''


application = webapp.WSGIApplication(
    [('/commentAdd', Add),
    ('/commentDelete', CommentDelete),
    ('/commentLike', CommentLike),
    ('/commentUnLike', CommentUnLike),
    ('/commentLikeView', CommentLikeView),
    ],)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()