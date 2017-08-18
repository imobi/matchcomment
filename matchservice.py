import datetime
import models

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

from protorpc import messages
from protorpc import message_types
from protorpc import remote

class Match(messages.Message):
  """Comment that gets posted to the service."""
  name = messages.StringField(1, required=True)
  matchStart = messages.StringField(2)

class Matchs(messages.Message):
  """Collection of Comments."""
  matchs = messages.MessageField(Match, 1, repeated=True)
  
class MatchService(remote.Service):
  """Comment service."""


  @remote.remote(message_types.VoidMessage, Matchs)
  def get_by_league(self, request):
    """Get comments from PostService.

    Returns the latest set of notes.
    """
    response = Matchs()
    response.matchs = []
    for match_model in Match.gql('ORDER BY when DESC').fetch(10):
      match = Match()
      match.name = match_model.name
      match.matchStart = datetime.datetime.strftime(match_model.matchStart,
                                             DATE_FORMAT).decode('utf-8')
      response.match.append(match)
    return response
