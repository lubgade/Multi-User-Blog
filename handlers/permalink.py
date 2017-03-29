from handler import Handler
from main import *
from main import CookieFunctions


class PermalinkHandler(Handler, CookieFunctions):
    def get(self, id):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user(cookie_val)
        else:
            user = ""
        e = Blog.get_blog_entry(id)
        if e:
            comments_list = Comment.get_comments_list(e, 0)
            self.render('permalink.html', e=e, id=id, cookie_val=cookie_val,
                        user=user.name, comments_list=comments_list)
        else:
            self.redirect('/blog')
