import os

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class FrontPage(Handler):
    def get(self):
        results = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        items = results.fetch(limit=10)
        self.render("frontpage.html", items = items)

class NewPost(Handler):
    def render_newpost(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            b = Blog(subject = subject, content = content)
            b.put()
            bid = b.key().id()

            self.redirect("/unit3/blog/%s" % bid)
        else:
            error = "we need both a subject and content"
            self.render_newpost(subject, content, error)

class BlogPage(Handler):
    def get(self, blog_id):
        key = db.Key.from_path('Blog', int(blog_id))
        item = db.get(key)
        if not item:
            self.error(404)
            return
        
        self.render("blogpage.html", title = item.subject, date = item.created.strftime("%b %d, %Y"), content = item.content)
