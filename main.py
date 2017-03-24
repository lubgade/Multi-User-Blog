import os
import jinja2
# noinspection PyUnresolvedReferences
import webapp2
# noinspection PyUnresolvedReferences
from google.appengine.ext import db
import re
import time
import string
import random
import hashlib
import hmac


os.environ['TZ'] = 'US/Eastern'
time.tzset()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

tags_title = ['h1', 'strong', 'b']
tags_content = ['em', 'strong', 'h1', 'b', 'br', 'p']

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

COOKIE_RE = re.compile(r'.+=;\s*Path=/')


def valid_cookie(cookie):
    return cookie and COOKIE_RE.match(cookie)


# Validating user input

def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASSWORD_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email)


# Password Hashing

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    val = h.split(",")
    return make_pw_hash(name, pw, val[1]) == h


# Cookie Validation

SECRET = 'iamsosecret'


class CookieFunctions(webapp2.RequestHandler):

    def hash_str(self, s):
        return hmac.new(SECRET, s).hexdigest()

    def make_secure_val(self, s):
        return "%s|%s" % (s, self.hash_str(s))

    def check_secure_val(self, h):
        result = h.split("|")
        if self.hash_str(result[0]) == result[1]:
            return result[0]

    def cookie_check(self):
        cookie_str = self.request.cookies.get("user_id")
        print cookie_str
        if cookie_str:
            cookie_val = self.check_secure_val(cookie_str)
            return cookie_val


from models.comment import Comment
from models.user import User
from models.blog import Blog
from models.loggedinusers import LoggedinUsers



from handlers.mainpage import MainPage
from handlers.newpost import NewpostHandler
from handlers.permalink import PermalinkHandler
from handlers.signup import SignUpHandler
from handlers.welcome import WelcomePageHandler
from handlers.login import LoginPageHandler
from handlers.logout import LogoutPageHandler
from handlers.editpost import EditPostHandler
from handlers.deletepost import DeletePostHandler
from handlers.editcomment import EditCommentHandler
from handlers.error import ErrorHandler
from handlers.newcomment import NewCommentHandler
from handlers.deletecomment import DeleteCommentHandler
from handlers.likepost import LikePostHandler
from handlers.dislikepost import DisLikePostHandler


app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/newpost', NewpostHandler),
                               ('/blog/(\d+)', PermalinkHandler),
                               ('/blog/signup', SignUpHandler),
                               ('/blog/welcome', WelcomePageHandler),
                               ('/blog/login', LoginPageHandler),
                               ('/blog/logout', LogoutPageHandler),
                               ('/blog/(\d+)/editpost', EditPostHandler),
                               ('/blog/(\d+)/deletepost', DeletePostHandler),
                               ('/blog/(\d+)/editcomment/(\d+)',
                                EditCommentHandler),
                               ('/blog/error', ErrorHandler),
                               ('/blog/(\d+)/newcomment', NewCommentHandler),
                               ('/blog/(\d+)/deletecomment/(\d+)',
                                DeleteCommentHandler),
                               ('/blog/(\d+)/like', LikePostHandler),
                               ('/blog/(\d+)/dislike', DisLikePostHandler)],
                              debug=True)
