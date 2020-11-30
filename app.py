""" write to a SQLite database with forms, templates
    add new record, delete a record, edit/update a record
    """

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import or_, func
from sqlalchemy.sql import text

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField, validators
from wtforms.validators import InputRequired, Length, Regexp, NumberRange, DataRequired
from datetime import date,datetime
import random
import itertools
from modules import *

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# Flask-Bootstrap requires this line
Bootstrap(app)

# the name of the database; add path if necessary
db_name = 'recipes_data.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

db_table='recipes_test'

# each table in the database needs a class to be created for it
# db.Model is required - don't change it
# identify all columns by name and data type
class Recipe(db.Model):
    __tablename__ = db_table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    style = db.Column(db.String)
    url = db.Column(db.String)
    ingredients = db.Column(db.String)
    instructions = db.Column(db.String)
    notes = db.Column(db.String)
    keywords = db.Column(db.String)
    updated_at = db.Column(db.String)
    image = db.Column(db.String)
    rating = db.Column(db.Integer)

    def __init__(self, id, name, style, url, ingredients, instructions, notes, keywords, updated_at, image, rating):
        self.id = id
        self.name = name
        self.style = style
        self.url = url
        self.ingredients = ingredients
        self.instructions = instructions
        self.notes = notes
        self.keywords = keywords
        self.updated_at = updated_at
        self.image = image
        self.rating = rating

# +++++++++++++++++++++++
# forms with Flask-WTF

# form for add_record and edit_or_delete
# each field includes validation requirements and messages
class AddRecord(FlaskForm):
    # hidden fields
    id_field = HiddenField()
    updated_at = HiddenField()
    
    # form entry fields
    name = StringField('Recipe name', [ InputRequired(),
        Regexp(r'^[1-9A-Za-z\s\-\']+$', message="Invalid recipe name"),
        Length(min=3, max=100, message="Invalid recipe name length")
        ])
    style = SelectField('Choose the sock style', [ InputRequired()],
        choices=[
        ('foo', 'Foo'),
        ('bar', 'Bar'),
        ('snafu', 'Snafu') ])
    url = StringField('URL for original recipe', validators=(validators.Optional(),validators.URL()))
    ingredients = StringField('Ingredients', validators=(validators.Optional(),))
    instructions = StringField('Instructions', validators=(validators.Optional(),))
    notes = StringField('notes', validators=(validators.Optional(),))
    keywords = StringField('keywords', validators=(validators.Optional(),))
    image = StringField('image', validators=(validators.Optional(),))
    rating = IntegerField('rating', validators=(validators.Optional(),validators.NumberRange(min=0, max=10, message="Rating must be an integer between 0 and 10")))

    submit = SubmitField('Add/Update Record')

# small form
class DeleteForm(FlaskForm):
    id_field = HiddenField()
    purpose = HiddenField()
    submit = SubmitField('Delete This Recipe')
    
# form for searching by ingredient
class IngredientSearchForm(FlaskForm):
    ingredient = StringField('Search by ingredient')
    submit = SubmitField('Submit')    

# +++++++++++++++++++++++
# routes

@app.route('/', methods=['GET', 'POST'])
def index():
    # get a list of unique values in the style column
    
    styles = Recipe.query.with_entities(Recipe.style).distinct()
    
    recipes_list_sorted = Recipe.query.order_by(Recipe.name).all()
    
    #ingredients are a little special because each recipe's "ingredients" field is a comma-separated text field
    ingredients = [i.ingredients for i in Recipe.query.with_entities(Recipe.ingredients).distinct()]
    a = [x.split(',') for x in ingredients]
    ingredients_list = [x.strip().lower() for x in list(itertools.chain.from_iterable(a)) if len(x)>0]
    ingredients_list_sorted = sorted(list(set(ingredients_list)))

    #searching by ingredient
    form = IngredientSearchForm()
    
    message = ""
    if form.validate_on_submit():
        ingredient = form.ingredient.data
        if ingredient.lower() in ingredients_list:
            # empty the form field
            form.ingredient.data = ""
            # redirect the browser to another route and template
            return redirect( url_for('ingredient', ingredient=ingredient) )
        
        else:
            message = "That ingredient is not in our database."
    
    return render_template('index.html'
                           , styles = styles
                           , ingredients = ingredients_list_sorted
                           , recipes = recipes_list_sorted
                           , form = form
                           , message = message
                          )
  
@app.route('/inventory/<style>')
def inventory(style):
    recipes = Recipe.query.filter_by(style=style).order_by(Recipe.name).all()
    return render_template('list.html', recipes=recipes, style=style)

@app.route('/all_recipes')
def all_recipes():
    recipes=Recipe.query.order_by(func.lower(Recipe.name)).all()
    return render_template('all_recipes.html', recipes=recipes)

# add a new recipe to the database
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
        id = random.randint(10000,99999)
        name = request.form['name']
        style = request.form['style']
        url = request.form['url']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        notes = request.form['notes']
        keywords = request.form['keywords']
        updated_at = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        image = request.form['image']
        rating = request.form['rating']
        # the data to be inserted into Recipe model - the table, recipes
        record = Recipe(id, name, style, url, ingredients, instructions)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        # create a message to send to the template
        message = f"The data for recipe {name} has been submitted."
        return render_template('add_record.html', message=message)
    else:
        # show validaton errors
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('add_record.html', form1=form1)

# select a record to edit or delete
@app.route('/select_record/<letters>')
def select_record(letters):
    # alphabetical lists by recipe name, chunked by letters between _ and _
    # .between() evaluates first letter of a string
    a,b = list(letters)
    if b=='Z': #between() is not inclusive??? So this is my super janky way to make it return recipes that start with "z"
        recipes = Recipe.query.filter(or_(func.lower(Recipe.name).like('z%'),Recipe.name.between(func.lower(a), func.lower(b)),Recipe.name.between(func.upper(a), func.upper(b)))).order_by(func.lower(Recipe.name)).all()
    else:
        recipes = Recipe.query.filter(or_(Recipe.name.between(func.lower(a), func.lower(b)),Recipe.name.between(func.upper(a), func.upper(b)))).order_by(func.lower(Recipe.name)).all()
    return render_template('select_record.html', recipes=recipes)

# edit or delete - come here from form in /select_record
@app.route('/edit_or_delete', methods=['POST'])
def edit_or_delete():
    id = request.form['id']
    choice = request.form['choice']
    recipe = Recipe.query.filter(Recipe.id == id).first()
    # two forms in this template
    form1 = AddRecord()
    form2 = DeleteForm()
    return render_template('edit_or_delete.html', recipe=recipe, form1=form1, form2=form2, choice=choice)

# result of delete - this function deletes the record
@app.route('/delete_result', methods=['POST'])
def delete_result():
    id = request.form['id_field']
    purpose = request.form['purpose']
    recipe = Recipe.query.filter(Recipe.id == id).first()
    if purpose == 'delete':
        db.session.delete(recipe)
        db.session.commit()
        message = f"The recipe {recipe.name} has been deleted from the database."
        return render_template('result.html', message=message)
    else:
        # this calls an error handler
        abort(405)

# result of edit - this function updates the record
@app.route('/edit_result', methods=['POST'])
def edit_result():
    id = request.form['id_field']
    # call up the record from the database
    recipe = Recipe.query.filter(Recipe.id == id).first()
    # update all values
    recipe.name = request.form['name']
    recipe.style = request.form['style']
    recipe.url = request.form['url']
    recipe.ingredients = request.form['ingredients']
    recipe.instructions = request.form['instructions']
    recipe.notes = request.form['notes']
    recipe.keywords = request.form['keywords']
    recipe.updated_at = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    recipe.image = request.form['image']
    recipe.rating = request.form['rating']
        
    # get today's date from function, above all the routes
    recipe.updated = stringdate()

    form1 = AddRecord()
    if form1.validate_on_submit():
        # update database record
        db.session.commit()
        # create a message to send to the template
        message = f"The data for recipe {recipe.name} has been updated."
        return render_template('result.html', message=message)
    else:
        # show validaton errors
        recipe.id = id
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('edit_or_delete.html', form1=form1, recipe=recipe, choice='edit')

    
@app.route('/ingredient/<ingredient>')
def ingredient(ingredient):
    try:
        recipes = Recipe.query.from_statement(text(f"SELECT * from {db_table} where ingredients like '%{ingredient}%'")).all() 
        return render_template('list.html', recipes=recipes, ingredient=ingredient)
    except Exception as e:
        return raiseError(e)
    
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    try:
        recipe = Recipe.query.filter_by(id=recipe_id).order_by(Recipe.name).all()
        try:
            image = recipe[0].image
        except:
            image = 'ohno.png'
        return render_template('recipe.html', recipe=recipe[0])
    except Exception as e:
        return raiseError(e)
    
# +++++++++++++++++++++++
# error routes
# https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/#registering-an-error-handler

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e), 404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e), 500

# +++++++++++++++++++++++

if __name__ == '__main__':
    app.run(debug=True)
