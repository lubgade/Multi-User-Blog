from handler import Handler
from main import *
from main import CookieFunctions


class DeletePostHandler(Handler, CookieFunctions):
    def get(self, id):
        e = Blog.get_blog_entry(id)
        if e:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user(cookie_val)
                if e.author.name == user.name:
                    e.delete()
                    self.render("deletepost.html")
                else:
                    error = "You are not authorized to delete this post"
                    self.render("choices_error.html", error=error, link=id)
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')
