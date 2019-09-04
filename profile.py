import webapp2
import jinja2
import os
import logging
from google.appengine.ext import ndb
from userentity import UserEntity
from tweetentity import TweetEntity
from google.appengine.api import search
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

from account_function import AccountFunction

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class ProfilePage(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_value = self.template_value(self)
        template_value["edit_tweet"] = False
        if self.request.params and "edit-tweet" in self.request.params:
            template_value["edit_tweet"] = True
            template_value["single_tweet"] = AccountFunction.get_tweet_by_id(self.request.params["edit-tweet"])

        if self.request.params and "delete-tweet" in self.request.params:
            template_value["delete_tweet"] = AccountFunction.delete_tweet(self.request.params["delete-tweet"])
            template_value['tweet_data'] = AccountFunction.get_tweets_for_current_user()

        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_value))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_value = self.template_value(self)
        template_value["edit_tweet"] = False
        if self.request.params and "edit-tweet" in self.request.params:
            template_value["edit_tweet"] = True
            template_value["single_tweet"] = AccountFunction.get_tweet_by_id(self.request.params["edit-tweet"])



        button = self.request.get("button")
        if button == "Search User":
            template_value['user_search'] = self.search_user(self)
        elif button == "Tweet":
            template_value['save_tweet'] = self.save_tweet(self)
        elif button == "Update Tweet":
            template_value['update_tweet'] = self.update_tweet(self)
        elif button == "Search Tweet":
            template_value['search_tweet'] = AccountFunction.search_tweet(self)

        template_value['tweet_data'] = AccountFunction.get_tweets_for_current_user()
        # logging.info(template_value)
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_value))


    def template_value(self, req):
        user = AccountFunction.getUser(req)
        tweet_data = AccountFunction.get_tweets_for_current_user()
        # logging.info(tweet_data)
        template_value = {
            'user': user,
            'following' : len(user['user'].following),
            'follow' : len(user['user'].follows),
            'tweet_data': tweet_data,
            'upload_url': blobstore.create_upload_url('/profile'),
            'images': images,
            'AccountFunction': AccountFunction,
        }

        # logging.info(user)
        return template_value

    def search_user(self, req):
        username = req.request.get("username")
        if not username:
            return {"message":"User name cannot empty", "status": False, "records":{}}

        record = UserEntity.query(UserEntity.user_name == username).fetch()
        if not record:
            return {"message": "User not available", "status": False, "records": {}}
        return {"message": "", "status": True, "records": record[0]}

    def save_tweet(self, req):
        text = req.request.get("text")
        file = req.get_uploads()
        if not text:
            return {"message": "Please enter tweet", "status": False, "records": {}}
        if len(text) > 280:
            return {"message": "Only 280 characters allowed", "status": False, "records": {}}

        upload = None
        if file:
            upload = file[0].key()
            info = blobstore.BlobReader(upload)
            if info.blob_info.content_type not in ['image/jpeg', 'image/png']:
                blobstore.delete(upload)
                return {"status": False, "message": "Only png PNG and JPEG can be uploaded"}

        userv= AccountFunction.current_user()
        tkey = AccountFunction.tweet_key(userv.user_name)
        Tweet = TweetEntity(id = tkey,tweet = text, user_name= userv.user_name, user_email = userv.email, tweet_image=upload)
        Tweet.put()
        userv.tweet_count = userv.tweet_count + 1
        userv.put()

        document = search.Document(
            doc_id=tkey,
            fields=[search.TextField(name='tweet', value=text),
                    search.TextField(name='user_name', value=userv.user_name)],
            language='en')

        search.Index(name='tweets').put(document)
        return {"message": "Tweet saved successfully", "status": True, "records": {}}

    def update_tweet(self, req):
        text = req.request.get("text")
        if not text:
            return {"message": "Please enter tweet", "status": False, "records": {}}
        if len(text) > 280:
            return {"message": "Only 280 characters allowed", "status": False, "records": {}}

        userv= AccountFunction.current_user()
        t_key = ndb.Key('TweetEntity', userv.user_name + '/' + req.request.params["edit-tweet"])
        tweet = t_key.get()
        tweet.tweet = text
        tweet.put()
        # userv.tweet_count = userv.tweet_count - 1
        # userv.put()

        index = search.Index('tweets')
        index.delete(userv.user_name + '/' + req.request.params["edit-tweet"])
        document = search.Document(
            doc_id= userv.user_name + '/' + req.request.params["edit-tweet"],
            fields=[search.TextField(name='tweet', value=text),
                    search.TextField(name='user_name', value=userv.user_name)],
            language='en')

        search.Index(name='tweets').put(document)
        return {"message": "Tweet updated successfully", "status": True, "records": {}}







app = webapp2.WSGIApplication([
    ('/profile', ProfilePage),
], debug=True)
