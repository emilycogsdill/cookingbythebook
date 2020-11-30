# cookingbythebook
It's a piece of cake to bake a pretty cake

## the heck is this

I was ambiguously unemployed for a bit ("independently working" as my mother likes to call it) so I put my shoulder to the wheel and figured out how Flask works. 

I was looking for a way to upgrade from my previous method of recipe tracking, which generally involved asking Greg to take some notes in a text doc. However, I am too much of a boomer to download a "mobile app" or some such. The obvious solution was to develop a web app. And here it is for all of you to see. 

The app is live here: https://cookingbythebook.herokuapp.com/

### what's goin on in here

* Recipe data is stored in a **SQLite database**, recipes_data.db.

* The app itself is, of course, powered by **Flask**.

* Web forms for data entry and retrieval in the app are powered by **Flask-WTF**. Not a family friendly name! But a very family friendly package!

### how'd you figure all that out, huh

This is an agglomeration of tutorials outlined here: https://python-adv-web-apps.readthedocs.io/en/latest/. This is apparently the _Python portion of Advanced Web Apps, a course for communications students at the University of Florida_. I found the accompanying Github repo to be extremely useful: https://github.com/macloo/python-adv-web-apps
