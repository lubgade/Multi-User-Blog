# noinspection PyUnresolvedReferences
from google.appengine.ext import db

class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    author = db.StringProperty()
    comments = db.ListProperty(int)
    liked_by = db.ListProperty(str)
    disliked_by = db.ListProperty(str)

    @property
    def likes(self):
        return len(self.liked_by)

    @property
    def dislikes(self):
        return len(self.disliked_by)

    @classmethod
    def get_blog_entry(cls, entry_id):
        key = db.Key.from_path('Blog', int(entry_id))
        return db.get(key)

