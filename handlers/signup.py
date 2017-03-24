from handler import Handler
from main import *
from main import CookieFunctions


class SignUpHandler(Handler, CookieFunctions):
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
                new_cookie_val = self.make_secure_val(str(user.key().id()))
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
