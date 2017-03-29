from handler import Handler
from main import *
from main import CookieFunctions


class DisLikePostHandler(Handler, CookieFunctions):
    def get(self, id):
        e = Blog.get_blog_entry(id)
        error = ""
        if e:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user(cookie_val)
                if e.author != user:
                    if user.name not in e.disliked_by:
                        if user.name not in e.liked_by:
                            e.disliked_by.append(user.name)
                            e.put()
                            self.redirect('/blog/%s' % str(id))
                        else:
                            error = "You can either like or dislike the post"
                    else:
                        error = "You cannot like a post more than once"
                else:
                    error = "You cannot dislike your own post"
                self.render("choices_error.html", error=error, link=id)
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')
