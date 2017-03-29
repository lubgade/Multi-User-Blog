from handler import Handler
from main import *
from main import CookieFunctions


class DeleteCommentHandler(Handler, CookieFunctions):
    def get(self, id, i):
        e = Blog.get_blog_entry(id)
        if e:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user(cookie_val)
                obj = Comment.get_comment(i)
                if obj:
                    if obj.comment_author == user.name:
                        obj.delete()
                        e.comments.remove(int(i))
                        e.put()
                        self.render("deletecomment.html", link=id)
                    else:
                        error = "You are not authorized to delete this comment"
                        self.render("choices_error.html", error=error, link=id)
                else:
                    self.redirect('/blog/%s' % str(id))
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')
