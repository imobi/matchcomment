from google.appengine.ext import db

class Sport(db.Model):
    type = db.StringProperty()
    description = db.StringProperty()
    #official = db.StringProperty() an actual official sport that is administered e.g. Cricket

    @staticmethod
    def load(sport):
        return Sport.gql('WHERE sport=:sport', sport=sport)
    
    def to_dict(self):
        tempdict1 = dict([(p, unicode(getattr(self, p))) for p in self.properties()])
        tempdict2 = {'key':unicode(self.key())}
        tempdict1.update(tempdict2)
        return tempdict1
# sport = Sport(type="rugby", description="Rugby").put()

#Rrepresents a League or Cup or Tournament
class League(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    sport = db.ReferenceProperty(Sport)
    country = db.StringProperty()
    city = db.StringProperty()
    is_official = db.IntegerProperty()
    user = db.UserProperty(required=True)#user that created, controls and manages this league profile
    teams = db.ListProperty(db.Key)#list of teams in this league
    #official = db.StringProperty() an actual official league that is administered e.g. Super Rugby
    twitterid = db.StringProperty() #twitter stream for the league e.g. wpclubrugby
    @staticmethod
    def bySport(sport):
        return League.gql('WHERE sport=:sport order by name ASC', sport=sport)

    def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#sport team profiles
class Team(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    league = db.ReferenceProperty(League) #should be removed, add team to list of teams property on league
    sport = db.ReferenceProperty(Sport)
    club = db.StringProperty() #db.ReferenceProperty(Club) #use flat club name instead of club object for now
    country = db.StringProperty()
    city = db.StringProperty()
    homeground = db.StringProperty()
    teamlogo = db.StringProperty() #user photobucket.com pic
    avatar = db.BlobProperty()
    facebookid = db.StringProperty()
    twitterid = db.StringProperty()
    user = db.UserProperty(required=True)#user that created, controls and manages this league profile
    #official = db.StringProperty() an actual official team that is administered e.g. Stormers

    @staticmethod
    def byLeague(league):
        return Team.gql('WHERE league=:league order by name desc', league=league)

    @staticmethod
    def byLeagueBySport(league, sport):
        return Team.gql('WHERE league=:league AND sport=:sport order by name desc', league=league, sport=sport)

    def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#Generic event that can be a sport match or debate that is commented on
class Event(db.Model):
    eventType = db.StringProperty() #match, debate, etc
    eventStart = db.DateTimeProperty(auto_now_add=False)
    eventOwner = db.UserProperty()

#Rrepresents a Match or Game or Race
class Match(Event):
    name = db.StringProperty()
    sideA = db.ReferenceProperty(Team, collection_name='hometeam')#db.StringProperty()
    sideB = db.ReferenceProperty(Team, collection_name='awayteam')#db.StringProperty()
    scoreA = db.StringProperty()
    scoreB = db.StringProperty()
    matchPeriod = db.StringProperty()# 1st / 2nd half
    matchStart = db.DateTimeProperty(auto_now_add=False)
    matchEnd = db.DateTimeProperty(auto_now_add=False) #to calculate the estimated match time to show whether match live
    league = db.ReferenceProperty(League)
    sport = db.ReferenceProperty(Sport) # to sort latest matches by sport
    country = db.StringProperty()
    city = db.StringProperty()
    venue = db.StringProperty()
    user = db.UserProperty(required=True)
    matchurl = db.StringProperty() #short / tiny url for game via http://tiny.cc
    matchViewers = db.ListProperty(db.Key) #list of users that checked into or commented on this match
    sideASupporters = db.ListProperty(db.Key)  #list of users that supported side A while watching this match
    sideBSupporters = db.ListProperty(db.Key) #list of users that supported side B while watching this match
    #official = db.StringProperty() an actual official league that is administered e.g. Super Rugby
    #user that created, controls and manages this league profile
    #location = db.StringProperty()#where the match is taking place

    @staticmethod
    def bySport(sport):
        return Match.gql('WHERE sport = :sport order by matchStart ASC', sport=sport)

    @staticmethod
    def bySportAfterNow(sport, matchStart):
        return Match.gql('WHERE matchStart > :1 AND sport = :2 ORDER BY matchStart ASC', matchStart, sport)

    @staticmethod
    def byLeague(league):
        return Match.gql('WHERE league = :league order by matchStart DESC', league=league)

    @staticmethod
    def byLeagueByTeam(league, team):
        return Match.gql('WHERE league = :league AND sideA = :team AND sideB = :team order by matchStart ASC', league=league, team=team)
    
    @staticmethod
    def byLeagueAfterNow(league, matchStart):
        return Match.gql('WHERE matchStart > :1 AND league = :2 ORDER BY matchStart ASC', matchStart, league)

    @staticmethod
    def byLeagueAfterNowByTeam(league, matchStart, team):
        return Match.gql('WHERE matchStart > :1 AND league = :2 AND sideA = :3 OR sideB = :3 ORDER BY matchStart ASC', matchStart, league, team)   

    def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#networks and supporter groups and clubs which users can join
class Network(db.Model):
  user = db.UserProperty(required=True)#user that created, controls and manages this network
  created = db.DateTimeProperty(auto_now_add=True)
  name = db.StringProperty()
  description = db.StringProperty()
  avatar = db.BlobProperty()

  def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#base user profile for a matchcomment user
class Profile(db.Model):
  user = db.UserProperty(required=True)
  registered = db.DateTimeProperty(auto_now_add=True)
  userType = db.StringProperty() #can be an administrator, fan, sport player, sport club, sport team
  name = db.StringProperty()
  surname = db.StringProperty()
  email = db.StringProperty()
  mobile = db.StringProperty()
  username = db.StringProperty()
  password = db.StringProperty()
  matchFavourites = db.ListProperty(db.Key)
  alias = db.StringProperty()
  sportPreference = db.ReferenceProperty(Sport) #make default None
  leaguePreference = db.ReferenceProperty(League) #make default None
  city = db.StringProperty()
  state = db.StringProperty()
  country = db.StringProperty()
  profilePicture = db.StringProperty() #user photobucket.com pic
  avatar = db.BlobProperty()
  gender = db.StringProperty()
  following = db.ListProperty(db.Key) #users you follow on matchcomment
  followers = db.ListProperty(db.Key) #users following you on matchcomment
  teams = db.ListProperty(db.Key) #connections to teams bookmarked by user
  leagues = db.ListProperty(db.Key) #connections to leagues bookmarked by user
  sports = db.ListProperty(db.Key) #connections to leagues bookmarked by user
  players = db.ListProperty(db.Key) #sportsmen or players the user follows
  networks = db.ListProperty(db.Key) #list of networks / groups the user belongs to
  facebookId = db.StringProperty() #facebook profile id
  facebookAccessToken = db.StringProperty() #access token issued by facebook with extended permissions for graph api
  loginMechanism = db.StringProperty() #matchcomment, gmail, facebook, twitter
  newsItemCount = db.StringProperty() #total news items to display default is 3

  @staticmethod
  def load(user):
    if user:
      profile = Profile.gql('WHERE user=:user', user=user).get()
      if profile:
        return profile
    return None

  @staticmethod
  def findProfile(userLogin,password):
    profile = Profile.gql('WHERE username=:userLogin AND password=:password', userLogin=userLogin, password=password).get()
    if profile:
        return profile
    return None

  @staticmethod
  def loadfacebookuser(facebookid):
    if facebookid:
      profile = Profile.gql('WHERE facebookid=:facebookid', facebookid=facebookid).get()
      if profile:
        return profile
    return None

  #see video on youtube for more info on counters http://www.youtube.com/watch?feature=player_embedded&v=Oh9_t5W6MTE
  @staticmethod
  def count_all(cls):
    entities = []
    for entity in cls.all():
        entities.append(entity)
    count = entities.__len__()
    return count

  def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#class to store data related to which team a user supported in a match
class TeamSupportedInMatch(db.Model):
  match = db.ReferenceProperty(Match)
  team = db.ReferenceProperty(Team)
  profile = db.ReferenceProperty(Profile)
  @staticmethod
  def getTeamForMatch(profile, match):
    return TeamSupportedInMatch.gql('WHERE profile = :1 AND match = :2', profile, match).get()

  def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])

#Comments or Stories or News taking place on matchcomment e.g. Joe joined Arsenal vs Manchester City
class Comment(db.Model):
  text = db.TextProperty(required=True)
  time = db.DateTimeProperty(auto_now_add=True)
  user = db.UserProperty(required=True)#make this a reference property to get user data for comment in html
  profile = db.ReferenceProperty(Profile)
  match = db.ReferenceProperty(Match)
  league = db.ReferenceProperty(League)#to search by league
  sport = db.ReferenceProperty(Sport)#to search by sport
  #team = db.ReferenceProperty(Team)#to search by team
  #player = db.ReferenceProperty(Player)#to search by team
  useralias = db.StringProperty()
  commenttype = db.StringProperty() # check in / opinion (like a fb status or tweet) prediction, referree decision, armcharir coaching, facebook, twitter, google, foursquare, buzz
  likes = db.ListProperty(db.Key)
  source = db.StringProperty() #if posted via another source e.g. twitter.com, facebook.com, arsenal.com
  #comments related to this comment
  #comments = db.ListProperty(db.Key)# list of comments on this related to Comment (fb status, tweet, link, photo, video, poll, rating, etc) which other users can comment on
  #teamKey = db.StringProperty(required=True)
  #locationCountry = db.StringProperty() 
  #locationCity = db.StringProperty()

  @staticmethod
  def byMatch(match):
    return Comment.gql('WHERE match=:match order by time desc', match=match)

  @staticmethod
  def byUser(user):
    return Comment.gql('WHERE user=:user order by time desc', user=user)

  @staticmethod
  def byProfile(profile):
    return Comment.gql('WHERE profile=:profile order by time desc', profile=profile)

  @staticmethod
  def byTimeDecending(total):
    comments = Comment.all().order('-time').fetch(total)
    return comments

  @staticmethod
  def bySport(sport, total):
      return Comment.gql('WHERE sport = :1 order by time desc', sport).fetch(total)

  @staticmethod
  def byLeague(league, total):
    return Comment.gql('WHERE league = :1 order by time desc', league).fetch(total)

  @staticmethod
  def count_all(cls):
    entities = []
    for entity in cls.all():
        entities.append(entity)
    count = entities.__len__()
    return count

  def to_dict(self):
       return dict([(property, unicode(getattr(self, property))) for property in self.properties()])


# add methods byFanFollowers, byFansFollowing, bySport, byTeam, byPlayer, byLeague
# see link on joins http://stackoverflow.com/questions/810303/without-joins-on-google-app-engine-does-your-data-have-to-exist-in-one-big-table
# http://turbomanage.wordpress.com/2010/01/25/how-to-do-joins-in-appengine/
# http://www.google.com/events/io/2009/sessions/BuildingScalableComplexApps.html
'''
Combining it to one big table is always an option, but it results unnecessarily large and redundant tables most of the time, thus it will make your app slow and hard to maintain.
You can also emulate a join, by iterating through the results of a query, and running a second query for each result found for the first query. If you have the SQL query
SELECT a.x FROM b INNER JOIN a ON a.y=b.y;
you can emulate this with something like this:
for b in db.GqlQuery("SELECT * FROM b"):
  for a in db.GqlQuery("SELECT * FROM a WHERE y=:1", b.y):
    print a.x
'''

#sport Club / franchise profiles
#class Club(db.Model):
#    name = db.StringProperty()
#    description = db.StringProperty()
#    creator = db.UserProperty(required=True)


#sport player profiles (players of team sports, individual sports like tennis, golf, athletics, motorsport, martial arts)
#DIFFERENT FROM TWITTER IN THAT ITS THE OFFICIAL PLAYER NAME and can only be assigned to the official player
class Player(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    creator = db.UserProperty(required=True)
    #teams = db.ListProperty(db.Key) #list of teams this player plays in
    team = db.ReferenceProperty(Team) #should be able to assign player multiple teams

#for news article aggregation from other sites related to the sport or league
class Newsfeed(db.Model):
  name = db.TextProperty(required=True)
  description = db.TextProperty()
  feeds = db.ListProperty(db.Key)
  user = db.UserProperty(required=True)
  league = db.ReferenceProperty(League)
  sport = db.ReferenceProperty(Sport)
  #match = db.ReferenceProperty(Match)
  #useralias = db.StringProperty()
#  teamKey = db.StringProperty(required=True)
#commenttype #referree decision, armcharir coaching

#for blog posts
class Article(db.Model):
  title = db.TextProperty(required=True)
  text = db.TextProperty(required=True)
  time = db.DateTimeProperty(auto_now_add=True)
  user = db.UserProperty(required=True)
  sport = db.ReferenceProperty(Sport)
  #match = db.ReferenceProperty(Match)
  #useralias = db.StringProperty()
#  teamKey = db.StringProperty(required=True)
#commenttype #referree decision, armcharir coaching

#media comments feed and page hosting for their live comments to plug into matchcomment an alternative to twitter and facebook
class Media(db.Model):
  name = db.StringProperty()
  mediaType = db.StringProperty() #tv, radio, magazine, newspaper, etc

#facebook user
class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

class UserRequest(db.Model):
    requestType = db.StringProperty() #sport, league, match, etc
    name = db.StringProperty() #sport, league, match, etc
    surname = db.StringProperty() #sport, league, match, etc
    email = db.StringProperty() #sport, league, match, etc
    country = db.StringProperty() #sport, league, match, etc
    city = db.StringProperty() #sport, league, match, etc
    email = db.StringProperty() #sport, league, match, etc

