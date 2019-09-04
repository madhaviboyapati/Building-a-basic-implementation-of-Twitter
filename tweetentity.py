from google.appengine.ext import ndb


class TweetEntity(ndb.Model):
    tweet = ndb.StringProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    tweet_image = ndb.BlobKeyProperty()
    user_name = ndb.StringProperty()
    user_email = ndb.StringProperty()