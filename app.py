from flask import Flask, render_template
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from modules import * 

app = Flask(__name__)

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
    names = get_names(recipes_list)
    form = NameForm()
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
    return render_template('lookup.html'
                           , names=names
                           , form=form
                           , message=message)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
