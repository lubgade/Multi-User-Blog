# noinspection PyUnresolvedReferences
from google.appengine.ext import db

class LoggedinUsers(db.Model):
    loggedinuser_id = db.StringProperty()
