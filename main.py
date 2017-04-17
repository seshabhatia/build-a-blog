import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now= True)

class NewPost(Handler):
    # handles newpost form submissions
    def render_entry_form(self, title="", entry="", error=""):
        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_entry_form()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Post(title=title, entry=entry)
            e.put()

            self.redirect("/blog/"+ str(e.key().id()))
        else:
            error = "Enter Title and Entry content!"
            self.render_entry_form(title, entry, error)

class BlogEntries(Handler):
    #handles the '/blog' webpage
    def render_entries(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, entry=entry, error=error, entries=entries)
    def get(self):
        self.render_entries()

class ViewPostHandler(Handler):
    #handle viewing single post by entity id
    def get(self, id):
        single_entry = Post.get_by_id(int(id))
        if single_entry:
            self.render("singlepost.html", single_entry=single_entry)
        else:
            error = "No Post Found for id entered = " + str(id)
            self.response.write(error)

app = webapp2.WSGIApplication([
    ('/', BlogEntries),
    ('/blog', BlogEntries),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
