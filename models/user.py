# noinspection PyUnresolvedReferences
from google.appengine.ext import db


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_user_name(cls, cookie_val):
        user = User.get_by_id(int(cookie_val))
        return user.name
