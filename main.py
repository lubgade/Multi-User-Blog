import os
import jinja2
# noinspection PyUnresolvedReferences
import webapp2
# noinspection PyUnresolvedReferences
from google.appengine.ext import db
import re
import string
import bleach
import random
import hashlib
import hmac


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

tags_title = ['h1', 'strong', 'b']
tags_content = ['em', 'strong', 'h1', 'b', 'br', 'p']

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

COOKIE_RE = re.compile(r'.+=;\s*Path=/')


def valid_cookie(cookie):
    return cookie and COOKIE_RE.match(cookie)


# Validating user input

def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASSWORD_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email)


# Password Hashing

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    val = h.split(",")
    return make_pw_hash(name, pw, val[1]) == h


# Cookie Validation

SECRET = 'iamsosecret'


def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    result = h.split("|")
    if hash_str(result[0]) == result[1]:
        return result[0]


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def cookie_check(self):
        cookie_str = self.request.cookies.get("user_id")
        if cookie_str:
            cookie_val = check_secure_val(cookie_str)
            return cookie_val


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()


class LoggedinUsers(db.Model):
    loggedinuser_id = db.StringProperty()


class Comment(db.Model):
    comment = db.TextProperty()
    comment_author = db.StringProperty()


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)
    author = db.StringProperty()
    comments = db.ListProperty(int)
    likes = db.IntegerProperty(int)
    dislikes = db.IntegerProperty(int)
    liked_by = db.ListProperty(str)
    disliked_by = db.ListProperty(str)


class NewpostHandler(Handler):
    def get(self):
        cookie_val = self.cookie_check()
        if cookie_val:
            user = User.get_by_id(int(cookie_val))
            self.render("newpost.html", cookie_val=cookie_val, user=user.name)
            return
        self.redirect('/blog/signup')

    def post(self):
        author = ""
        val = ""
        cookie_val = self.cookie_check()
        if cookie_val:
            val = User.get_by_id(int(cookie_val))
            author = val.name
        else:
            cookie_val = ""

        subject = self.request.get("subject")
        subject = bleach.clean(subject, tags=tags_title)
        content = self.request.get("content")
        content = content.replace('\n', '<br>')
        content = bleach.clean(content, tags=tags_content)

        if subject and content:
            entry = Blog(subject=subject, content=content, author=author,
                         likes=0, dislikes=0, liked_by=[""], disliked_by=[""])
            entry.put()
            id = entry.key().id()
            self.redirect('/blog/%s' % str(id))
        else:
            error = "subject and content, please"
            self.render("newpost.html", error=error, subject=subject,
                        content=content, cookie_val=cookie_val, user=val.name)


class MainPage(Handler):
    def get(self):
        cookie_val = ""
        user = ""
        entries = db.GqlQuery(" SELECT * FROM Blog ORDER BY created DESC "
                              "LIMIT 6")
        cookie_val = self.cookie_check()
        if cookie_val:
            val = User.get_by_id(int(cookie_val))
            user = val.name
        self.render('blog.html', subject="", content="", entries=entries,
                    cookie_val=cookie_val, user=user)


class PermalinkHandler(Handler):
    def get(self, id):
        cookie_val = ""
        cookie_val = self.cookie_check()
        if cookie_val:
            val = User.get_by_id(int(cookie_val))
            user = val.name
        else:
            user = ""
        key = db.Key.from_path('Blog', int(id))
        e = db.get(key)
        if e:
            comments_list = []
            for k in e.comments:
                comments_list.append(Comment.get_by_id(int(k)))
            self.render('permalink.html', e=e, id=id, cookie_val=cookie_val,
                        user=user, comments_list=comments_list)
        else:
            self.error(404)
            return

    def post(self, id):
        e = Blog.get_by_id(int(id))
        error = ""
        user = ""
        cookie_val = ""
        cookie_val = self.cookie_check()
        if cookie_val:
            val = User.get_by_id(int(cookie_val))
            user = val.name
            form_name = self.request.get("formname")
            if form_name == "commentform":
                text_comment = self.request.get("comments")
                text_comment = text_comment.replace('\n', '<br>')
                text_comment = db.Text(text_comment)
                text_comment = db.Text(bleach.clean(text_comment,
                                                    tags=tags_content))
                new_comment = Comment(comment=text_comment,
                                      comment_author=user)
                new_comment.put()
                id = new_comment.key().id()
                e.comments.append(id)
            elif form_name == "likeform":
                if e.author != user:
                    if user not in e.liked_by:
                        e.likes += 1
                        e.liked_by.append(user)
                    else:
                        error = "You cannot like the post more than once"
                else:
                    error = "You cannot like your own post"
            elif form_name == "dislikeform":
                if e.author != user:
                    if user not in e.disliked_by:
                        e.dislikes += 1
                        e.disliked_by.append(user)
                    else:
                        error = "You cannot dislike the post more than once"
                else:
                    error = "You cannot dislike your own post"
            elif form_name == "editform":
                if e.author == user:
                    self.redirect('/blog/%s/editpost' % str(id))
                else:
                    error = "You are not authorized to edit this post"
            elif form_name == "deleteform":
                if e.author == user:
                    self.redirect('/blog/%s/deletepost' % str(id))
                else:
                    error = "You are not authorized to delete this post"
            elif form_name == "editcomment":
                i = self.request.get("comment_id")
                e_comment = Comment.get_by_id(int(i))
                if i:
                    if e_comment.comment_author == user:
                        self.redirect('/blog/%s/editcomment/%s' % (str(id),
                                                                   str(i)))
                    else:
                        error = "You are not authorized to edit this comment"
            elif form_name == "deletecomment":
                i = self.request.get("comment_id")
                if i:
                    obj = Comment.get_by_id(int(i))
                    if obj.comment_author == user:
                        e.comments.remove(int(i))
                        obj.delete()
                    else:
                        error = "You are not authorized to delete this comment"
        else:
            self.redirect('/blog/login')
        comments_list = []
        comments_list = filter(None, comments_list)
        for k in e.comments:
            if k:
                comments_list.append(Comment.get_by_id(int(k)))
        e.comments = filter(None, e.comments)
        e.put()
        self.render('permalink.html', e=e, error=error, cookie_val=cookie_val,
                    user=user, comments_list=comments_list)


class SignUpHandler(Handler):
    def get(self):
        self.render("signuptemplate.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""

        if not valid_email(email) and email:
            email_error = "Invalid email"

        if not valid_username(username):
            username_error = "Invalid Username"

        if not valid_password(password):
            password_error = "Invalid Password"

        if password != verify:
            verify_error = "Passwords do not match"

        if not valid_password(verify) and verify:
            verify_error = "Invalid Password"

        if not email_error and not username_error and not password_error and \
                not verify_error:
            query = User.gql("WHERE name = :1", username)

            if query.get():
                self.redirect('/blog/error')

            else:
                name = self.request.get("username")
                password = self.request.get("password")
                email = self.request.get("email")
                user = User(name=name, password=make_pw_hash(name, password),
                            email=email)
                user.put()
                new_cookie_val = make_secure_val(str(user.key().id()))
                self.response.headers.add_header('Set-Cookie',
                                                 'user_id = %s Path = /'
                                                 % new_cookie_val)
                new_login = LoggedinUsers(loggedinuser_id=new_cookie_val)
                new_login.put()
                self.redirect('/blog/welcome')
        else:
            self.render("signuptemplate.html", username=username,
                        password=password, verify=verify, email=email,
                        username_error=username_error,
                        password_error=password_error,
                        verify_error=verify_error,
                        email_error=email_error)


class WelcomePageHandler(Handler):
    def get(self):
        cookie_val = self.cookie_check()
        if cookie_val:
            val = User.get_by_id(int(cookie_val))
            user_name = val.name
            self.render("welcometemplate.html", name=user_name, user=user_name,
                        cookie_val=cookie_val)
        else:
            self.redirect('/blog/signup')


class LoginPageHandler(Handler):
    def get(self):
        self.render("logintemplate.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        username_error = ""
        password_error = ""

        if not valid_username(username):
            username_error = "Invalid Username"

        if not valid_password(password):
            password_error = "Invalid Password"

        if not username_error and not password_error:
            query = User.gql("WHERE name = :1", username)
            result = query.get()

            if result:
                id = result.key().id()
                h = result.password
                n = result.name
                if valid_pw(n, password, h):
                    new_cookie_val = make_secure_val(str(id))
                    self.response.headers.add_header('Set-Cookie',
                                                     'user_id = %s Path = /'
                                                     % new_cookie_val)
                    new_login = LoggedinUsers(loggedinuser_id=new_cookie_val)
                    new_login.put()
                    self.redirect('/blog/welcome')
                else:
                    password_error = "Invalid Password"
                    self.render("logintemplate.html", username=username,
                                password_error=password_error)
            else:
                self.redirect('/blog/signup')

        else:
            self.render("logintemplate.html", username=username,
                        password=password, username_error=username_error,
                        password_error=password_error)


class LogoutPageHandler(Handler):
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


class EditPostHandler(Handler):
    def get(self, id):
        if id:
            key = db.Key.from_path('Blog', int(id))
            e = db.get(key)
            content = e.content
            content = content.replace("<br>", "\n")
            cookie_val = self.cookie_check()
            user = User.get_by_id(int(cookie_val))
            if cookie_val:
                self.render("editpost.html", subject=e.subject, content=content,
                            user=e.author, cookie_val=cookie_val)
            else:
                error = "You are not authorized to edit this post"
                self.render('permalink.html', e=e, error=error,
                            cookie_val=cookie_val, user=user.name)

    def post(self, id):
        if id:
            key = db.Key.from_path('Blog', int(id))
            e = db.get(key)
            e.subject = self.request.get("subject")
            e.subject = bleach.clean(e.subject, tags=tags_title)
            content = self.request.get("content")
            e.content = content.replace("\n", "<br>")
            e.content = bleach.clean(e.content, tags=tags_content)
            e.put()
            self.redirect('/blog/%s' % str(id))


class DeletePostHandler(Handler):
    def get(self, id):
        if id:
            key = db.Key.from_path('Blog', int(id))
            e = db.get(key)
            e.delete()
            self.render("deletepost.html")


class EditCommentHandler(Handler):
    def get(self, id, i):
        if id:
            cookie_val = self.cookie_check()
            user = User.get_by_id(int(cookie_val))
            entry = Blog.get_by_id(int(id))
            subject = entry.subject
            content = entry.content
            ed_comment = Comment.get_by_id(int(i))
            ed_comment.comment = ed_comment.comment.replace("<br>", "\n")
            if ed_comment:
                self.render("editcomment.html", subject=subject,
                            content=content, author=entry.author,
                            comments=ed_comment.comment, user=user.name,
                            cookie_val=cookie_val, created=entry.created)

    def post(self, id, i):
        if id:
            ed_comment = Comment.get_by_id(int(i))
            ed_comment.comment = self.request.get("comments")
            ed_comment.comment = ed_comment.comment.replace("\n", "<br>")
            ed_comment.comment = bleach.clean(ed_comment.comment,
                                              tags=tags_content)
            ed_comment.put()
            self.redirect('/blog/%s' % str(id))


class ErrorHandler(Handler):
    def get(self):
        self.render("error.html")


app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/newpost', NewpostHandler),
                               ('/blog/(\d+)', PermalinkHandler),
                               ('/blog/signup', SignUpHandler),
                               ('/blog/welcome', WelcomePageHandler),
                               ('/blog/login', LoginPageHandler),
                               ('/blog/logout', LogoutPageHandler),
                               ('/blog/(\d+)/editpost', EditPostHandler),
                               ('/blog/(\d+)/deletepost', DeletePostHandler),
                               ('/blog/(\d+)/editcomment/(\d+)',
                                EditCommentHandler),
                               ('/blog/error', ErrorHandler)], debug=True)
