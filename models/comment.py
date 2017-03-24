# noinspection PyUnresolvedReferences
from google.appengine.ext import db


class Comment(db.Model):
    comment = db.TextProperty()
    comment_author = db.StringProperty()

    @classmethod
    def get_comment(cls, comm_id):
        key = db.Key.from_path('Comment', int(comm_id))
        return db.get(key)
