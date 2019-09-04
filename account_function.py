from userentity import UserEntity
from tweetentity import TweetEntity
from google.appengine.api import users
from google.appengine.ext import ndb
import time;
import logging
from google.appengine.api import search
from google.appengine.api import images
from google.appengine.ext import blobstore

class AccountFunction:

    @classmethod
    def getUser(cls, request):
        user = users.get_current_user()
        url = ""
        url_string = ""
        my_user = ""

        if user:
            url = users.create_logout_url("/")
            url_string = 'logout'

            user_key = ndb.Key('UserEntity', user.email())
            my_user = user_key.get()

            if my_user == None:
                myuser = UserEntity(id=user.email(), email = user.email())
                myuser.put()
        else:
            url = users.create_login_url(request.request.uri)
            url_string = 'login'

        return {"login_url":url, "login_text":url_string,"user":my_user}

    @classmethod
    def save_username(cls, username):
        user = users.get_current_user()
        user_key = ndb.Key('UserEntity', user.email())
        my_user = user_key.get()
        my_user.user_name = username
        my_user.put()

    @classmethod
    def tweet_key(cls, username):
        ts = time.time()
        crr_time = int(ts)
        return username + "/" + str(crr_time)

    @classmethod
    def current_user(cls):
        user = users.get_current_user()
        user_key = ndb.Key('UserEntity', user.email())
        my_user = user_key.get()
        return my_user

    @classmethod
    def tweets_by_user(cls):
        pass

    @classmethod
    def user_by_username(cls, user_name):
        pass

    @classmethod
    def update_profile(cls, req):
        name = req.request.get("name")
        bio = req.request.get("bio")
        if len(bio) > 280:
            return {"status": False, "message": "Bio only allow 280 characters ", "data": {}}
        user = users.get_current_user()
        user_key = ndb.Key('UserEntity', user.email())
        my_user = user_key.get()
        my_user.name = name
        my_user.bio = bio
        my_user.put()
        return {"status": True, "message": "Profile Update successfully", "data": {}}

    @classmethod
    def get_following_flag(cls, req):
        current_user = AccountFunction.current_user()
        username = req.request.params['user']
        query = UserEntity.query(UserEntity.user_name == current_user.user_name)
        query = query.fetch()[0]
        logging.info(query)
        if (not query.following):
            return {"follow_text": "Follow"}
        if username in query.following:
            return {"follow_text": "UnFollow"}
        else:
            return {"follow_text": "Follow"}

    @classmethod
    def change_follow_status(cls,req):
        user = AccountFunction.current_user()
        username = req.request.params['user']
        status = req.request.get("follow")
        if status == "Follow":
            user.following.append(username)
            user.put()

            query = UserEntity.query(UserEntity.user_name == username)
            query = query.fetch()[0]
            query.follows.append(username)
            query.put()
            return {"status": True, "message": "You are now following @" + username, "data": {}}
        else:
            user.following.remove(username)
            user.put()

            query = UserEntity.query(UserEntity.user_name == username)
            query = query.fetch()[0]
            query.follows.remove(username)
            query.put()
            return {"status": True, "message": "You are now unfollowing @" + username, "data": {}}

    @classmethod
    def get_tweets_by_username(cls, username):
        query = TweetEntity.query(TweetEntity.user_name == username).order(-TweetEntity.date_added)
        query = query.fetch()
        if not query:
            return {"status": False, "message": "No tweets posted yet" + username, "data": {}}
        return {"status": True, "message": "" + username, "data": query}

    @classmethod
    def get_user_by_ueraname(cls, username):
        query = UserEntity.query(UserEntity.user_name == username)
        query = query.fetch()[0]
        return query

    @classmethod
    def get_tweets_for_current_user(cls):
        user = AccountFunction.current_user()
        user.following.append(user.user_name)
        tweet = TweetEntity.query(TweetEntity.user_name.IN(user.following)).order(-TweetEntity.date_added).fetch(50)
        user.following.remove(user.user_name)
        return tweet

    @classmethod
    def get_tweet_by_id(cls, id):
        user = AccountFunction.current_user()
        key = ndb.Key('TweetEntity', user.user_name + '/' + id)
        tweet = key.get()
        if tweet:
            return tweet
        return None

    @classmethod
    def delete_tweet(cls, id):
        user = AccountFunction.current_user()
        key = ndb.Key('TweetEntity', user.user_name + '/' + id)
        tweet = key.get()
        if tweet:
            key.delete()

            user.tweet_count = user.tweet_count - 1
            user.put()
            return True
        return False

    @classmethod
    def search_tweet(cls, req):
        index = search.Index('tweets')
        tweet = req.request.get('text').lower().rstrip()
        logging.info(tweet)
        if len(tweet) == 0:
            return {"status": False, "message":"Search field cannot empty", "data" : {}}
        search_query = search.Query(query_string=tweet)
        logging.info("---------------------")
        logging.info(search_query)
        tweets = []
        for document in index.search(search_query):
            val = AccountFunction.get_tweet_by_key(document.doc_id)
            if val:
                tweets.append(val)
        if not tweets:
            return {"status": False, "message": "No tweets available", "data": {}}
        len(tweets)
        return {"status": True, "message": "", "data": tweets}

    @classmethod
    def format_time(cls, time):
        datetime_object = time.strftime('%Y-%m-%d %H:%M:%S')
        return datetime_object

    @classmethod
    def get_tweet_by_key(cls, id):
        key = ndb.Key('TweetEntity', id)
        return key.get()













