from handler import Handler
# noinspection PyUnresolvedReferences
from google.appengine.ext import db
from main import CookieFunctions
from main import *


class MainPage(Handler, CookieFunctions):
    def get(self):
        user = ""
        entries = db.GqlQuery(" SELECT * FROM Blog ORDER BY created DESC "
                              "LIMIT 6")
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user_name(cookie_val)
        self.render('blog.html', subject="", content="", entries=entries,
                    user=user, cookie_val=cookie_val)
