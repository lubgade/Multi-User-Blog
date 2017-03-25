from handler import Handler
from main import *
from main import CookieFunctions
import bleach


class EditCommentHandler(Handler, CookieFunctions):
    def get(self, id, i):
        entry = Blog.get_blog_entry(id)
        if entry:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user_name(cookie_val)
                subject = entry.subject
                content = entry.content
                ed_comment = Comment.get_comment(i)
                ed_comment.comment = ed_comment.comment.replace("<br>", "\n")
                if ed_comment:
                    if ed_comment.comment_author == user:
                        comments_list = Comment.get_comments_list(entry, i)
                        self.render("editcomment.html", subject=subject,
                                    content=content, author=entry.author,
                                    comments=ed_comment.comment, user=user,
                                    cookie_val=cookie_val,
                                    created=entry.created, entry=entry,
                                    link=id, comments_list=comments_list)
                    else:
                        error = "You are not authorized to edit this comment"
                        self.render("choices_error.html", error=error, link=id)
                else:
                    self.redirect('/blog/%s' % str(id))
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')

    def post(self, id, i):
        entry = Blog.get_blog_entry(id)
        if entry:
            cookie_val = self.cookie_check()
            if cookie_val:
                user = User.get_user_name(cookie_val)
                ed_comment = Comment.get_comment(i)
                if ed_comment:
                    ed_comment.comment = self.request.get("comments")
                    if ed_comment.comment:
                        ed_comment.comment = ed_comment.comment.replace("\n",
                                                                        "<br>")
                        ed_comment.comment = bleach.clean(ed_comment.comment,
                                                          tags=tags_content)
                        ed_comment.put()
                        self.redirect('/blog/%s' % str(id))
                    else:
                        error = "Enter the comment please"
                        comments_list = Comment.get_comments_list(entry, i)
                        self.render("editcomment.html", entry=entry,
                                    subject=entry.subject,
                                    content=entry.content,
                                    cookie_val=cookie_val, user=user,
                                    error=error, link=id,
                                    comments_list=comments_list)
                else:
                    self.redirect('/blog/%s' % str(id))
            else:
                self.redirect('/blog/login')
        else:
            self.redirect('/blog')
