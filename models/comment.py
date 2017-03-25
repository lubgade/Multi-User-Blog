# noinspection PyUnresolvedReferences
from google.appengine.ext import db


class Comment(db.Model):
    comment = db.TextProperty()
    comment_author = db.StringProperty()

    @classmethod
    def get_comment(cls, comm_id):
        key = db.Key.from_path('Comment', int(comm_id))
        return db.get(key)

    @classmethod
    def get_comments_list(cls, e, i):
        comments_list = []
        if i:
            for k in e.comments:
                if int(k) != int(i):
                    comments_list.append(Comment.get_comment(k))
        else:
            for k in e.comments:
                if k:
                    comments_list.append(Comment.get_comment(k))
        return comments_list
