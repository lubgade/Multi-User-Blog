from main import *
from handler import Handler
from main import CookieFunctions
import bleach
# noinspection PyUnresolvedReferences
from google.appengine.ext import db


class NewpostHandler(Handler, CookieFunctions):
    def get(self):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user(cookie_val)
            self.render("newpost.html", cookie_val=cookie_val, user=user.name)
            return
        self.redirect('/blog/signup')

    def post(self):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user(cookie_val)

            subject = self.request.get("subject")
            subject = bleach.clean(subject, tags=tags_title)
            content = self.request.get("content")
            content = content.replace('\n', '<br>')
            content = bleach.clean(content, tags=tags_content)
            author = user

            if subject and content:
                entry = Blog(subject=subject, content=content,author=author,
                             liked_by=[], disliked_by=[])
                entry.put()
                id = entry.key().id()
                self.redirect('/blog/%s' % str(id))
            else:
                error = "subject and content, please"
                self.render("newpost.html", error=error, subject=subject,
                            content=content, cookie_val=cookie_val,
                            user=user.name)
        else:
            self.redirect('/blog/login')