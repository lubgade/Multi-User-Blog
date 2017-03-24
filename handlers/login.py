from handler import Handler
from main import *
from main import CookieFunctions


class LoginPageHandler(Handler, CookieFunctions):
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
                    new_cookie_val = self.make_secure_val(str(id))
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
