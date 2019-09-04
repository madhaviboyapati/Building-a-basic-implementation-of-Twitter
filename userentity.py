from google.appengine.ext import ndb


class UserEntity(ndb.Model):
    email = ndb.StringProperty()
    user_name = ndb.StringProperty()
    following = ndb.StringProperty(repeated=True)
    follows = ndb.StringProperty(repeated=True)
    name = ndb.StringProperty(default="")
    bio = ndb.StringProperty(default="")
    tweet_count = ndb.IntegerProperty(default=0)
    joined = ndb.DateTimeProperty(auto_now_add=True)