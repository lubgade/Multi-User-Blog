# noinspection PyUnresolvedReferences
from google.appengine.ext import db


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_user(cls, cookie_val):
        key = db.Key.from_path('User', int(cookie_val))
        return db.get(key)
