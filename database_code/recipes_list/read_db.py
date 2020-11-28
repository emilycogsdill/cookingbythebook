""" read from a SQLite database and return data to templates """

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import itertools
from sqlalchemy.sql import text


app = Flask(__name__)

# Flask-Bootstrap requires this line
Bootstrap(app)

# the name of the database; add path if necessary
db_name = 'recipes_data.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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
    URL = db.Column(db.String)
    title = db.Column(db.String)
    keywords = db.Column(db.String)
    ingredients = db.Column(db.String)
    instructions = db.Column(db.String)
    notes = db.Column(db.String)
    make_again = db.Column(db.Integer)
    things_to_try = db.Column(db.String)
    image = db.Column(db.String)
    category = db.Column(db.String)

#routes
@app.route('/')
def index():
    try:
        categories = Recipe.query.with_entities(Recipe.category).distinct()
        categories_list = sorted([c.category for c in categories if c.category!=None])
        
        #ingredients are a little special because each recipe's "ingredients" field is a comma-separated text field
        ingredients = [i.ingredients for i in Recipe.query.with_entities(Recipe.ingredients).distinct()]
        a = [x.split(',') for x in ingredients]
        ingredients_list = sorted([x.strip() for x in list(itertools.chain.from_iterable(a))])

        return render_template('index.html'
                               , categories=categories_list
                               , ingredients = ingredients_list
                              )
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

@app.route('/ingredient/<ingredient>')
def ingredient(ingredient):
    try:
        recipes = Recipe.query.from_statement(text(f"SELECT * from recipes where ingredients like '%{ingredient}%'")).all()
        
        #output_text = '<ul>'
        #for r in recipes:
        #    output_text += '<li>' + r.title + ', last prepared on '  + r.timestamp_prepared + ' (id = ' + str(r.id) + ')</li>'
        #output_text += '</ul>'
        #return output_text
        #
        #return output
        
        return render_template('list.html', recipes=recipes, ingredient=ingredient)
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    
@app.route('/inventory/<category>')
def inventory(category):
    try:
        recipes = Recipe.query.filter_by(category=category).order_by(Recipe.title).all()
        return render_template('list.html', recipes=recipes, category=category)
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


if __name__ == '__main__':
    app.run(debug=True)
