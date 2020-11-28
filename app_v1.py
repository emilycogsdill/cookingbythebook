from flask import Flask, render_template
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy.sql import text
from modules import * 
import os


app = Flask(__name__)

db_name = 'recipes_data.db'
    
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    name = StringField('Which recipe do you want to look up?', validators=[DataRequired()])
    submit = SubmitField('Go fish (but please don\'t - fish are our friends)')
    



# create a list of dicts from a CSV
recipes_list = convert_to_dict("recipe_info.csv")

# create a list of tuples in which the first item is the number
# (id) and the second item is the recipe name (Title)
pairs_list = []
for p in recipes_list:
    pairs_list.append( (p['id'], p['Title']) )

# first route

@app.route('/')
def index():
    return render_template('index.html', pairs=pairs_list, the_title="Recipes Index")

# second route

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def detail(id):
    try:
        recipe_dict = recipes_list[int(id) - 1]
    except:
        return f"<h1>Invalid recipe id: {id}</h1>"
    # a little bonus function, imported on line 2 above
    ord = make_ordinal( int(id) )
    form = NameForm()
    names = get_names(recipes_list)
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        if any(name.lower() in x for x in names):
            # empty the form field
            form.name.data = ""
            id = get_id(recipes_list, name)
            # redirect the browser to another route and template
            return redirect( url_for('detail', id=id) )
            #message = f"you searched for {name.lower()}. That recipe has id = {id}"
        else:
            message = f"you searched for {name.lower()}. That recipe is not in our database: {names}. The HECK is wrong with you"
    return render_template('recipe.html'
                           , names=names
                           , recipe=recipe_dict
                           , ord=ord
                           , the_title=recipe_dict['Title']
                           , form=form
                          )

@app.route('/lookup', methods=['GET', 'POST']) #for more on flask forms: https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.htmls
def lookup():
    results_list=[]
    names = get_names(recipes_list)
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        
        results_list = []
        
        #get all recipe ids and titles
        #TODO: make a single function that returns tuples
        ids_list = get_ids_list(recipes_list, name)
        titles_list = get_recipe_titles_from_ids(recipes_list, ids_list)
        
        for t in range(len(ids_list)):
            results_list.append( (ids_list[t], titles_list[t]))
            
    return render_template('lookup.html'
                           , names=names
                           , form=form
                           , message=message
                           , results=results_list)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
