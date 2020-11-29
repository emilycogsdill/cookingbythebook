""" 
cobbled together from tutorials at https://python-adv-web-apps.readthedocs.io

https://python-adv-web-apps.readthedocs.io/en/latest/flask_db3.html

"""

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlalchemy.sql import text
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField, DateField, validators
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from datetime import date, datetime


from modules import *
import itertools
import random


app = Flask(__name__)

# Flask-Bootstrap requires this line
Bootstrap(app)

# the name of the database; add path if necessary
db_name = 'recipes_data.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

# each table in the database needs a class to be created for it
# db.Model is required - don't change it
# identify all columns by name and data type
class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    timestamp_entered = db.Column(db.String)
    timestamp_prepared = db.Column(db.String)
    #url = db.Column(db.String)
    title = db.Column(db.String)
    keywords = db.Column(db.String)
    ingredients = db.Column(db.String)
    instructions = db.Column(db.String)
    notes = db.Column(db.String)
    make_again = db.Column(db.String)
    things_to_try = db.Column(db.String)
    image = db.Column(db.String)
    category = db.Column(db.String)

    
    def __init__(self, id, timestamp_entered, timestamp_prepared, title, keywords, ingredients, instructions, notes, make_again, things_to_try, image, category):
        self.id = id
        self.timestamp_entered = timestamp_entered
        self.timestamp_prepared = timestamp_prepared
        #self.url = url
        self.title = title
        self.keywords = keywords
        self.ingredients = ingredients
        self.instructions = instructions
        self.notes = notes
        self.make_again = make_again
        self.things_to_try = things_to_try
        self.image = image
        self.category = category

        
# +++++++++++++++++++++++
# forms with Flask-WTF

# form for add_record and edit_or_delete
# each field includes validation requirements and messages
class AddRecord(FlaskForm):
    # id used only by update/edit
    id = HiddenField()
    timestamp_entered = HiddenField()
    # make this get the current timestamp    timestamp_entered = 

    timestamp_prepared = DateField('When did you make this? (M/D/YYYY)', format='%m/%d/%Y', validators=(validators.Optional(),))
    
    url = StringField('URL for original recipe', validators=(validators.Optional(),validators.URL()))

    title = StringField('Recipe name')
    keywords = StringField('Keywords', [
        Length(min=0, max=5000, message="C'mon, put something at least")
        ])
    ingredients = StringField('Ingredients', validators=(validators.Optional(),))
    instructions = StringField('Instructions', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\'\/]+$', message="Invalid entry"),
        Length(min=0, max=5000, message="C'mon, put something at least")
        ])
    notes = StringField('Notes', validators=(validators.Optional(),))
    make_again = SelectField('Would make again?', [ InputRequired()],
        choices=[ ('Yes', 'Yes')
                 , ('Maybe', 'Maybe')
                 , ('No', 'No')])
    things_to_try = StringField('Things to try in the future?', validators=(validators.Optional(),))
    image = StringField('Image name? idk make this an upload field someday', validators=(validators.Optional(),))
    category = SelectField('What kind of strat is this?', [ InputRequired()],
        choices=[ ('Discrete', 'Discrete')
                 , ('Continuous', 'Continuous')
                 , ('Mysterious', 'Mysterious')])
    # updated - date - handled in the route
    updated = HiddenField()
    submit = SubmitField('Add/Update Record')

    
# small form
class DeleteForm(FlaskForm):
    id_field = HiddenField()
    purpose = HiddenField()
    submit = SubmitField('Delete This Recipe, thumbs down emoji')


# +++++++++++++++++++++++

        
#routes
@app.route('/')
def index():
    try:
        recipes_list_sorted = Recipe.query.order_by(Recipe.title).all()
        
        categories = Recipe.query.with_entities(Recipe.category).distinct()
        categories_list_sorted = sorted([c.category for c in categories if c.category!=None])
        
        #ingredients are a little special because each recipe's "ingredients" field is a comma-separated text field
        ingredients = [i.ingredients for i in Recipe.query.with_entities(Recipe.ingredients).distinct()]
        a = [x.split(',') for x in ingredients]
        ingredients_list = [x.strip() for x in list(itertools.chain.from_iterable(a)) if len(x)>0]
        ingredients_list_sorted = sorted(list(set(ingredients_list)))

        return render_template('index.html'
                               , categories = categories_list_sorted
                               , ingredients = ingredients_list_sorted
                               , recipes = recipes_list_sorted
                              )
    except Exception as e:
        return raiseError(e)

# add a new recipe to the database
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
        
        id = random.randint(10000,99999)
        timestamp_prepared = request.form['timestamp_prepared']
        url = request.form['url']
        title = request.form['title']
        keywords = request.form['keywords']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        notes = request.form['notes']
        make_again = request.form['make_again']
        things_to_try = request.form['things_to_try']
        image = request.form['image']
        category = request.form['category']
        
        # get today's date from function, above all the routes
        timestamp_entered = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        
        # the data to be inserted into Sock model - the table, socks
        record = Recipe(id, timestamp_entered, timestamp_prepared, title, keywords, ingredients, instructions, notes, make_again, things_to_try, image, category)
        
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        
        # create a message to send to the template
        message = f"The data for recipe {title} has been submitted."
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
    
@app.route('/ingredient/<ingredient>')
def ingredient(ingredient):
    try:
        recipes = Recipe.query.from_statement(text(f"SELECT * from recipes where ingredients like '%{ingredient}%'")).all() 
        return render_template('list.html', recipes=recipes, ingredient=ingredient)
    except Exception as e:
        return raiseError(e)
    
@app.route('/inventory/<category>')
def inventory(category):
    try:
        recipes = Recipe.query.filter_by(category=category).order_by(Recipe.title).all()
        return render_template('list.html', recipes=recipes, category=category)
    except Exception as e:
        return raiseError(e)
    

@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    try:
        recipe = Recipe.query.filter_by(id=recipe_id).order_by(Recipe.title).all()
        try:
            image = recipe[0].image
        except:
            image = 'pr40.jpg'
        return render_template('recipe.html', recipe=recipe[0])
    except Exception as e:
        return raiseError(e)


if __name__ == '__main__':
    app.run(debug=True)
