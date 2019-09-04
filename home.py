import webapp2
import jinja2
import os
import logging
from google.appengine.ext import ndb
import logging

from account_function import AccountFunction

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        AccountFunction.getUser(self)
        template_value = self.get_template_value(self)

        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_value))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_value = self.get_template_value(self)
        # logging.info(self.request.get("username"))

        AccountFunction.save_username(self.request.get("username"))
        user = AccountFunction.getUser(self)
        if user['user'] and user['user'].user_name:
            self.redirect('/profile')
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_value))
        
    def get_template_value(self, req):
        user = AccountFunction.getUser(req)

        if user['user'] and user['user'].user_name:
            req.redirect('/profile')

        template_value = {
            'user': user
        }
        
        return template_value


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
