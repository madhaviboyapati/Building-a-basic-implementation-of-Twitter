import webapp2
import jinja2
import os
import logging
from google.appengine.ext import ndb
from userentity import UserEntity
from tweetentity import TweetEntity
from google.appengine.api import images

from account_function import AccountFunction

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class ShowProfile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_value = self.template_value(self)
        current_user = AccountFunction.current_user()
        if current_user.user_name == self.request.params["user"]:
            return self.redirect("/profile")

        # logging.info(self.request.params)
        # params = self.request.params
        # if params:
        #     params['user']
        #
        # template_value["username"] =  params['user']

        template = JINJA_ENVIRONMENT.get_template('show_profile.html')
        self.response.write(template.render(template_value))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'


        button = self.request.get("button")
        data = AccountFunction.change_follow_status(self)
        template_value = self.template_value(self)
        template_value['data'] = data
        # if button == "Search User":
        #     template_value['user_search'] =  self.search_user(self)
        # elif button == "Tweet":
        #     template_value['save_tweet'] = self.save_tweet(self)

        template = JINJA_ENVIRONMENT.get_template('show_profile.html')
        self.response.write(template.render(template_value))


    def template_value(self, req):
        user = AccountFunction.getUser(req)
        params = req.request.params

        if params:
            params['user']

        template_value = {
            'user': user,
            'username':params['user'],
            'status':AccountFunction.get_following_flag(req),
            'tweets':AccountFunction.get_tweets_by_username(params['user']),
            'profile_info':AccountFunction.get_user_by_ueraname(params['user']),
            'followers':len(AccountFunction.get_user_by_ueraname(params['user']).follows),
            'following':len(AccountFunction.get_user_by_ueraname(params['user']).following),
            'images': images,
            'AccountFunction': AccountFunction,
        }

        return template_value



app = webapp2.WSGIApplication([
    ('/show-profile', ShowProfile),
], debug=True)
