"""
functions to be imported into the presidents Flask app
"""

import csv

def convert_to_dict(filename):
    """
    Convert a CSV file to a list of Python dictionaries
    """
    # open a CSV file - note - must have column headings in top row
    datafile = open(filename, newline='')

    # create DictReader object
    my_reader = csv.DictReader(datafile)

    # create a regular Python list containing dicts
    list_of_dicts = list(my_reader)

    # close original csv file
    datafile.close()

    # return the list
    return list_of_dicts


def make_ordinal(num):
    """
    Create an ordinal (1st, 2nd, etc.) from a number.
    """
    base = num % 10
    if base in [0,4,5,6,7,8,9] or num in [11,12,13]:
        ext = "th"
    elif base == 1:
        ext = "st"
    elif base == 2:
        ext = "nd"
    else:
        ext = "rd"
    return str(num) + ext

# tryouts
def test_make_ordinal():
    for i in range(1,46):
        print(make_ordinal(i))

def search_the_list(list):
    for item in list:
        if "Whig" in item['Party']:
            print(item['President'] + " was a Whig.")
    for k in list[0].keys():
        print(k)

        
        
# retrieve all the names from the dataset and put them into a list
def get_names(source):
    names = []
    for row in source:
        # lowercase all the names for better searching
        name = row["Title"].lower()
        names.append(name)
    return sorted(names)

# find the row that matches the id in the URL, retrieve name and photo
def get_recipe(source, id):
    for row in source:
        if id == str( row["id"] ):
            name = row["name"]
            photo = row["photo"]
            # change number to string
            id = str(id)
            # return these if id is valid
            return id, name, photo
    # return these if id is not valid - not a great solution, but simple
    return "Unknown", "Unknown", ""

# find the row that matches the name in the form and retrieve matching id
def get_id(source, name):
    for row in source:
        # lower() makes the string all lowercase
        if name.lower() in row["Title"].lower():
            id = row["id"]
            # change number to string
            id = str(id)
            # return id if name is valid
            return id
    # return these if id is not valid - not a great solution, but simple
    return "Unknown"
    

# find the row that matches the name in the form and retrieve matching id
def get_ids_list(source, name):
    output_list=[]
    for row in source:
        # lower() makes the string all lowercase
        if name.lower() in row["Title"].lower():
            id = row["id"]
            # change number to string
            id = str(id)
            # return id if name is valid
            output_list.append(id)
    # return these if id is not valid - not a great solution, but simple
    return(output_list)

def get_recipe_titles_from_ids(source, ids_list):
    titles_list=[]
    for id_val in ids_list:
        recipe=list(filter(lambda recipe: recipe['id'] == id_val, source))[0]['Title']
        titles_list.append(recipe)
    return titles_list