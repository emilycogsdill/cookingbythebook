from flask import Flask, render_template, request
from modules import convert_to_dict, make_ordinal

gay = Flask(__name__)
application = gay

@gay.route("/")
def home():
    return "Sweet home"

@gay.route("/some-route")
def some_route():
    return "on the default subdomain (generally, www, or unguarded)"

@gay.route("/", subdomain="blog")
def blog_home():
    return "Sweet blog"

@gay.route("/<page>", subdomain="blog")
def blog_page(page):
    return "can be dynamic: {}".format(page)

# keep this as is
if __name__ == '__main__':
    gay.run(debug=True)
