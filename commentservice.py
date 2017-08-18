#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Comment service implementation.

This module contains all the protocol buffer and service definitions
necessary for the Comment service.
"""

import base64
import sys

from google.appengine.ext import db

from protorpc import descriptor
from protorpc import message_types
from protorpc import messages
from protorpc import protobuf
from protorpc import remote

import models

class CommentInfo(messages.Message):
  """Comment that gets posted to the service."""
  text = messages.StringField(1, required=True)
  # match = messages.StringField(2, required=True)
  # when = messages.StringField(3)
  
  
class AddCommentRequest(messages.Message):
  """Request to add a new Comment to library.

  Fields:
    text: The comment body to add
    match: The match the comment is for
  """
  text = messages.StringField(1, required=True)
  # match = messages.StringField(2, required=True)


class AddCommentResponse(messages.Message):
  """Response sent after creation of new artist in library.

  Fields:
    comment_id: Unique opaque ID of new comment.
  """
  comment_id = messages.StringField(1, required=True)
  
class SearchCommentsRequest(messages.Message):
  """Comments search request.

  Fields:
    continuation: Continuation from the response of a previous call to
      search_comments remote method.
    fetch_size: Maximum number of records to retrieve.
    match_id: Restrict search to comments of single artist.
  """

  continuation = messages.StringField(1)
  fetch_size = messages.IntegerField(2, default=10)
  # match_id = messages.StringField(3, default='')


class SearchCommentsResponse(messages.Message):
  """Response from searching comments.

  Fields:
    comments: Comments found from search up to fetch_size.
    continuation: Opaque string that can be used with a new search request
      that will continue finding new albums where this response left off.
      Will not be set if there were no results from the search or fewer
      albums were returned in the response than requested, indicating the end
      of the query.
  """

  comments = messages.MessageField(CommentInfo, 1, repeated=True)
  continuation = messages.StringField(2)
  
class CommentService(remote.Service):
  """Comment service."""

  __file_set = None
  
  def __comment_from_model(self, comment_model):
    """Helper that copies an Comment model to an Comment message.

    Args:
      comment_model: model.Comment instance to convert in to an CommentInfo
        message.

    Returns:
      New CommentInfo message with contents of comment_model copied in to it.
    """
    match_id = model.Comment.match.get_value_for_datastore(match_model)
    
    return CommentInfo(comment_id=unicode(comment_model.key()),
                  match=match_id)
    
  @classmethod
  def __search_info(cls,
                    request,
                    info_class,
                    model_to_message,
                    customize_query=None):
    """Search over an Info subclass.

    Since all search request classes are very similar, it's possible to
    generalize how to do searches over them.

    Args:
      request: Search request received from client.
      info_class: The model.Info subclass to search.
      model_to_method: Function (model) -> message that transforms an instance
        of info_class in to the appropriate messages.Message subclass.
      customize_query: Function (request, query) -> None that adds additional
        filters to Datastore query based on specifics of that search message.

    Returns:
      Tuple (results, continuation):
        results: A list of messages satisfying the parameters of the request.
          None if there are no results.
        continuation: Continuation string for response if there are more
          results available.  None if there are no more results available.
    """
    # TODO(rafek): fetch_size from this request should take priority
    # over what is stored in continuation.
    if request.continuation:
      encoded_search, continuation = request.continuation.split(':', 1)
      decoded_search = base64.urlsafe_b64decode(encoded_search.encode('utf-8'))
      request = protobuf.decode_message(type(request), decoded_search)
    else:
      continuation = None
      encoded_search = unicode(base64.urlsafe_b64encode(
          protobuf.encode_message(request)))

    text = request.text

    query = info_class.search(text)
    query.order('time')
    if customize_query:
      customize_query(request, query)

    if continuation:
      # TODO(rafek): Pure query cursors are not safe for model with
      # query restrictions.  Would technically need to be encrypted.
      query.with_cursor(continuation)

    fetch_size = request.fetch_size

    model_instance = query.fetch(fetch_size)
    results = None
    continuation = None
    if model_instance:
      results = [model_to_message(i) for i in model_instance]
      if len(model_instance) == fetch_size:
        cursor = query.cursor()
        continuation = u'%s:%s' % (encoded_search, query.cursor())

    return results, continuation

  @remote.method(AddCommentRequest, AddCommentResponse)
  def add_comment(self, request):
    """Add comment to library."""
    comment_text = request.text
    def do_add():
      comment = model.Comment(text=comment_text, match=comment_match)
      comment.put()
      return comment
    comment = db.run_in_transaction(do_add)

    return AddCommentResponse(comment_id = unicode(comment.key()))

  @remote.method(SearchCommentsRequest, SearchCommentsResponse)
  def search_comments(self, request):
    """Search for comments."""
    def customize_query(request, query):
      if request.match_id:
        query.filter('match', db.Key(request.match_id))

    response = SearchCommentsResponse()
    results, continuation = self.__search_info(request,
                                               model.Comment,
                                               self.__comment_from_model,
                                               customize_query)
    return SearchCommentsResponse(comments=results or None,
                                continuation=continuation or None)