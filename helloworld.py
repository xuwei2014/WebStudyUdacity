import webapp2
import cgi

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

class MainPage(webapp2.RequestHandler):
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
        self.response.write(form % {'textstr' : text})

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form();

    def post(self):
        text = self.request.get('text')
        self.write_form(cgi.escape(self.rot13(text), quote=True));

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
