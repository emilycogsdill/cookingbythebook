from flask import Flask, render_template
from modules import convert_to_dict, make_ordinal

app = Flask(__name__)
application = app

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

@app.route('/recipe/<id>')
def detail(id):
    try:
        recipe_dict = recipes_list[int(id) - 1]
    except:
        return f"<h1>Invalid recipe id: {id}</h1>"
    # a little bonus function, imported on line 2 above
    ord = make_ordinal( int(id) )
    return render_template('recipe.html'
                           , recipe=recipe_dict
                           , ord=ord
                           , the_title=recipe_dict['Title']
                          )


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
