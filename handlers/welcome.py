from handler import Handler
from main import *
from main import CookieFunctions


class WelcomePageHandler(Handler, CookieFunctions):
    def get(self):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user_name(cookie_val)
            self.render("welcometemplate.html", name=user, user=user,
                        cookie_val=cookie_val)
        else:
            self.redirect('/blog/signup')
