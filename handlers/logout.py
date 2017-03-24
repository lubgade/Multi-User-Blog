from handler import Handler
from main import CookieFunctions
from main import *


class LogoutPageHandler(Handler, CookieFunctions):
    def get(self):
        cookie_str = self.request.cookies.get("user_id")
        if cookie_str:
            query = LoggedinUsers.gql("WHERE loggedinuser_id= :1", cookie_str)
            if query:
                result = query.get()
                result.delete()
                self.response.headers.add_header('Set-Cookie',
                                                 'user_id = ; Path = /blog')
        self.redirect('/blog')
