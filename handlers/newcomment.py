from handler import Handler
from main import *
# noinspection PyUnresolvedReferences
from google.appengine.ext import db
from main import CookieFunctions
import bleach


class NewCommentHandler(Handler, CookieFunctions):
    def get(self, id):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user_name(cookie_val)
            e = Blog.get_blog_entry(id)
            if e:
                self.render('newcomment.html', e=e, id=id,
                            cookie_val=cookie_val, user=user)
            else:
                self.redirect('/blog')
        else:
            self.redirect('/blog/login')

    def post(self, id):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_user_name(cookie_val)
            e = Blog.get_blog_entry(id)
            if e:
                text_comment = self.request.get("comments")
                text_comment = text_comment.replace('\n', '<br>')
                text_comment = db.Text(text_comment)
                text_comment = db.Text(bleach.clean(text_comment,
                                                    tags=tags_content))
                new_comment = Comment(comment=text_comment,
                                      comment_author=user)
                new_comment.put()
                i = new_comment.key().id()
                e.comments.append(i)
                e.put()
                self.redirect('/blog/%s' % str(id))
            else:
                self.redirect('/blog')
        else:
            self.redirect('/blog/login')
