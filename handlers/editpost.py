from handler import Handler
from main import *
from main import CookieFunctions
import bleach


class EditPostHandler(Handler, CookieFunctions):
    def get(self, id):
        e = Blog.get_blog_entry(id)
        if e:
            content = e.content
            content = content.replace("<br>", "\n")
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user(cookie_val)
                if e.author.name == user.name:
                    self.render("editpost.html", subject=e.subject,
                                content=content, user=user.name,
                                cookie_val=cookie_val, e=e, link=id)
                else:
                    error = "You are not authorized to edit this post"
                    self.render("choices_error.html", error=error, link=id)
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')

    def post(self, id):
        e = Blog.get_blog_entry(id)
        if e:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user(cookie_val)
                subject = self.request.get("subject")
                content = self.request.get("content")
                if subject and content:
                    e.subject = bleach.clean(subject, tags=tags_title)
                    e.content = content.replace("\n", "<br>")
                    e.content = bleach.clean(e.content, tags=tags_content)
                    e.put()
                    self.redirect('/blog/%s' % str(id))
                else:
                    error = "subject and content, please"
                    self.render("editpost.html", error=error, subject=subject,
                                content=content, cookie_val=cookie_val,
                                user=user.name, link=id)
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')
