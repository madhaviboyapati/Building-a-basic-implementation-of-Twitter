import webapp2
import jinja2
import os
import logging

from account_function import AccountFunction

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
class editProfile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = AccountFunction.getUser(self)
        template_value = self.get_tempate_values(self)

        template = JINJA_ENVIRONMENT.get_template('edit_profile.html')
        self.response.write(template.render(template_value))

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_value = self.get_tempate_values(self)
        template_value["data"] = AccountFunction.update_profile(self)

        template = JINJA_ENVIRONMENT.get_template('edit_profile.html')
        self.response.write(template.render(template_value))

    def get_tempate_values(self,req):
        user = AccountFunction.getUser(req)
        logging.info(user['user'])
        template_value = {
            'user': user,
            'following': len(user['user'].following),
            'follow': len(user['user'].follows),
        }
        return template_value


app = webapp2.WSGIApplication([
    ('/editprofile', editProfile),
], debug=True)
