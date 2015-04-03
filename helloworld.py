import webapp2
import cgi
import re
import hmac

from blog import *
from google.appengine.ext import db

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Hello, Udacity!")

class ROT13(webapp2.RequestHandler):
    form = """
    <form method="post">
        <label>
            <b>Enter some text to ROT13:</b>
            <br>
            <br>
            <textarea name="text">%(textstr)s</textarea>
        </label>
        <br>
        <br>
        <input type="submit">
    </form>
    """

    def rot(self, c, off = 13):
        res = c
        if c.islower():
            res = chr((ord(c) + off - 97) % 26 + 97)
        elif c.isupper():
            res =  chr((ord(c) + off - 65) % 26 + 65)
    
        return res
    
    def rot13(self, s):
        res = ""
        for i in range(len(s)):
            res += self.rot(s[i])
    
        return res

    def write_form(self, text = ""):
        self.response.write(self.form % {'textstr' : text})

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        text = self.request.get('text')
        self.write_form(cgi.escape(self.rot13(text), quote=True))


SECRET = "xuweiweb"

def make_hash_name(name):
    h = hmac.new(str(name), SECRET).hexdigest()
    return "%s|%s" % (name, h)

def check_name(name, h):
    return make_hash_name(name) == h

class User(db.Model):
    name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()

class SignUp(webapp2.RequestHandler):
    form = """
    <form method="post">
        <label>
            <b>Signup</b>
        </label>
        <br>
        <br>
        <label>
            Username
            <input name="username" value="%(user)s">
        </label>
        <div style="color: red">%(user_err)s</div>

        <label>
            Password
            <input name="password" type="password" value="%(pass)s">
        </label>
        <div style="color: red">%(pass_err)s</div>

        <label>
            Verify Password
            <input name="verify" type="password" value="%(verify)s">
        </label>
        <div style="color: red">%(verify_err)s</div>

        <label>
            Email(optional)
            <input name="email" value="%(email)s">
        </label>
        <div style="color: red">%(email_err)s</div>

        <input type="submit">
    </form>
    """

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


    def write_form(self, user="", passwd="", verify="", email="",
                         user_err="", pass_err="", verify_err="", email_err=""):
        self.response.write(self.form % {'user' : user,
                                         'pass' : passwd,
                                         'verify' : verify,
                                         'email' : email,
                                         'user_err' : user_err,
                                         'pass_err' : pass_err,
                                         'verify_err' : verify_err,
                                         'email_err' : email_err,
                                         })

    def get(self):
        self.write_form()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        user_err = ""
        pass_err = ""
        verify_err = ""
        email_err = ""

        if not self.USER_RE.match(username) :
            user_err = "That's not a valid username."

        if not self.PASS_RE.match(password) :
            pass_err = "That wasn't a valid password."
        else :
            if password != verify :
                verify_err = "Your passwords didn't match."

        if email and (not self.MAIL_RE.match(email)):
            email_err = "That's not a valid email."


        results = db.GqlQuery('SELECT * FROM User WHERE name=:1', username)
        item = results.get()
        if item:
            user_err = "The name have been used."

        if user_err == "" and pass_err == "" and verify_err == "" and email_err == "" :
            u = User(name = username, password = password, email = email)
            u.put()

            self.response.headers.add_header('Set-Cookie', 'name=%s;Path=/' % str(make_hash_name(username)))
            self.redirect("/blog/welcome")
        else :
            self.write_form(username, password, verify, email,
                        user_err, pass_err, verify_err, email_err)

class Welcome(webapp2.RequestHandler):
    def get(self):
        h = self.request.cookies.get('name')
        name = h.split('|')[0]
        if check_name(name, h):
            self.response.write("Welcome, %s!" % name);
        else:
            self.redirect("/blog/signup")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/unit2/rot13', ROT13),
    ('/blog/signup', SignUp),
    ('/blog/welcome', Welcome),
    ('/blog', FrontPage),
    ('/blog/newpost', NewPost),
    (r'/blog/(\d+)', BlogPage),
], debug=True)
