from handler import Handler
from main import *
from main import CookieFunctions



class PermalinkHandler(Handler, CookieFunctions):
    def get(self, id):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user_name(cookie_val)
        else:
            user = ""
        e = Blog.get_blog_entry(id)
        comments_list = []
        if e:
            for k in e.comments:
                if e.comments:
                    comments_list.append(Comment.get_comment(k))
            self.render('permalink.html', e=e, id=id, cookie_val=cookie_val,
                        user=user, comments_list=comments_list)
        else:
            self.redirect('/blog')
