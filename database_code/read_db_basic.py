""" read from a SQLite database and return data """

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
        recipes = Recipe.query.filter_by(category='Continuous').order_by(Recipe.title).all()
        recipe_text = '<ul>'
        for recipe in recipes:
            recipe_text += '<li>' + recipe.title + ', prepared on ' + recipe.timestamp_prepared + '</li>'
        recipe_text += '</ul>'
        return recipe_text
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

if __name__ == '__main__':
    app.run(debug=True)
