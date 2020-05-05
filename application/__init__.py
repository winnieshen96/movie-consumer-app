from flask import Flask, render_template, request, json, session
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, Integer, String, Float
# import flask_whooshalchemy as wa
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'person.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# app.config['WHOOSH_BASE'] = 'whoosh'

# TODO change it to read from csv file
genres_to_select = ['isAdult', 'Action',
       'Adventure', 'Drama', 'Fantasy', 'Sci-Fi', 'Thriller', 'Animation',
       'Comedy', 'Family', 'Crime', 'Horror', 'History', 'Romance', 'Mystery',
       'Musical', 'Documentary', 'Adult', 'War', 'Biography', 'Western',
       'Sport', 'Music', 'News', 'Film-Noir']

@app.route("/")
@app.route("/index")
def index():
    session['directors'] = []
    session['writers'] = []
    session['genres'] = []
    return render_template("index.html", genres_to_select=genres_to_select)

@app.route('/directorsearch', methods=['GET', 'POST'])
def directorsearch():
    # db = SQLAlchemy(app)
    conn = sqlite3.connect('person.db', check_same_thread=False)
    c = conn.cursor()
    # director = Person.query.whoosh_search(request.form.get("director")).all()[0]
    search_name = request.form.get("director").strip()
    # print(search_name)
    c.execute('''SELECT name, person_id, roi FROM PERSON WHERE name LIKE ?''', [search_name])
    director = c.fetchall()[0]
    # print(director)
    directors = session.get('directors', None)
    if director not in directors:
        directors.append(director)
    session['directors'] = directors
    return render_template("index.html", directors=session.get('directors', None), writers=session.get('writers', None), genres_to_select=genres_to_select, genres=session.get('genres', None))

@app.route('/writersearch', methods=['GET', 'POST'])
def writersearch():
    # writer = Person.query.whoosh_search(request.form.get("writer")).all()[0]
    # TODO save the writer for later classify
    # db = SQLAlchemy(app)
    conn = sqlite3.connect('person.db', check_same_thread=False)
    c = conn.cursor()
    search_name = request.form.get("writer").strip()
    c.execute('''SELECT name, person_id, roi FROM PERSON WHERE name LIKE ?''', [search_name])
    writer = c.fetchall()[0]
    writers = session.get('writers', None)
    if writer not in writers:
        writers.append(writer)
    session['writers'] = writers
    return render_template("index.html", directors=session.get('directors', None), writers=session.get('writers', None), genres_to_select=genres_to_select, genres=session.get('genres', None))

@app.route('/genreselect', methods=['GET', 'POST'])
def genreselect():
    genres_selected = request.form.getlist('genres')
    genres = session.get('genres', None)
    for genre in genres_selected:
        if genre not in genres:
            genres.append(genre)
    session['genres'] = genres
    return render_template("index.html", directors=session.get('directors', None), writers=session.get('writers', None), genres_to_select=genres_to_select, genres=session.get('genres', None))

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    session.clear()
    session['directors'] = []
    session['writers'] = []
    session['genres'] = []
    return render_template("index.html", genres_to_select=genres_to_select)

@app.route("/roiclassify", methods=['GET', 'POST'])
def roiclassify():

    # TODO incoming plot prediction feature extract form inputs
    # plot = request.form.get("plot")
    
    # select low_performed people
    threshold = 2
    low_performed = []
    directors = session.get('directors', None)
    writers = session.get('writers', None)
    for person in directors:
        if person[2] < threshold:
            low_performed.append(person)
    for person in writers:
        if person[2] < threshold:
            low_performed.append(person)
    #url for irisservice
    # url = "http://localhost:5001/api"
    url = "https://movie-model-app.herokuapp.com/api"

    # create json from form inputs
    data = json.dumps({"director": session.get('directors', None), "writer": session.get('writers', None), "genres": session.get('genres', None)})

    # post json to url
    results =  requests.post(url,data)
    results.encoding = results.apparent_encoding
    results = json.loads(results.text)
    prediction = results['prediction']
    scores = {}
    for score in results['scores']:
        scores[score] = round(float(results['scores'][score]), 3)*100

    #send features and prediction result to index.html for display
    return render_template("index.html", directors=session.get('directors', None), writers=session.get('writers', None), genres=session.get('genres', None), genres_to_select=genres_to_select, prediction=prediction, scores=scores, low_performed=low_performed)


# # database models
# class Person(db.Model):
#     __searchable__ = ['person_id', 'name']
#     generated_id = Column(Integer, primary_key=True)
#     person_id = Column(String)
#     roi = Column(Float)
#     name = Column(String)

# wa.whoosh_index(app, Person)  # pass in the class we want to index