from flask import Flask, render_template, request, json
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, Integer, String, Float
# import flask_whooshalchemy as wa
import sqlite3
import os
import requests

app = Flask(__name__)
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'person.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# app.config['WHOOSH_BASE'] = 'whoosh'

# db = SQLAlchemy(app)
conn = sqlite3.connect('person.db', check_same_thread=False)
c = conn.cursor()

directors = []
writers = []
# TODO change it to read from csv file
genres_to_select = ['isAdult', 'Action',
       'Adventure', 'Drama', 'Fantasy', 'Sci-Fi', 'Thriller', 'Animation',
       'Comedy', 'Family', 'Crime', 'Horror', 'History', 'Romance', 'Mystery',
       'Musical', 'Documentary', 'Adult', 'War', 'Biography', 'Western',
       'Sport', 'Music', 'News', 'Film-Noir']
genres = []

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", genres_to_select=genres_to_select)


@app.route('/directorsearch', methods=['GET', 'POST'])
def directorsearch():
    # director = Person.query.whoosh_search(request.form.get("director")).all()[0]
    search_name = request.form.get("director").strip()
    # print(search_name)
    c.execute('''SELECT name, person_id, roi FROM PERSON WHERE name LIKE ?''', [search_name])
    director = c.fetchall()[0]
    # print(director)
    if director not in directors:
        directors.append(director)
    return render_template("index.html", directors=directors, writers=writers, genres_to_select=genres_to_select, genres=genres)


@app.route('/writersearch', methods=['GET', 'POST'])
def writersearch():
    # writer = Person.query.whoosh_search(request.form.get("writer")).all()[0]
    # TODO save the writer for later classify
    search_name = request.form.get("writer").strip()
    c.execute('''SELECT name, person_id, roi FROM PERSON WHERE name LIKE ?''', [search_name])
    writer = c.fetchall()[0]
    if writer not in writers:
        writers.append(writer)
    return render_template("index.html", directors=directors, writers=writers, genres_to_select=genres_to_select, genres=genres)

@app.route('/genreselect', methods=['GET', 'POST'])
def genreselect():
    genres_selected = request.form.getlist('genres')
    for genre in genres_selected:
        if genre not in genres:
            genres.append(genre)
    return render_template("index.html", directors=directors, writers=writers, genres_to_select=genres_to_select, genres=genres)


@app.route("/roiclassify", methods=['GET', 'POST'])
def roiclassify():

    # TODO incoming plot prediction feature extract form inputs
    # plot = request.form.get("plot")
    
    #url for irisservice
    #url = "http://localhost:5000/api"
    url = "https://irismodel-app.herokuapp.com/api"

    #create json from form inputs
    # data = json.dumps({"plot": plot, "director": directors, "writer": writers})
    data = json.dumps({"director": directors, "writer": writers})

    #post json to url
    results =  requests.post(url,data)
    
    #send features and prediction result to index.html for display
    return render_template("index.html", plot = plot, directors=directors, writers=writers, results=results.content.decode('UTF-8'))


# # database models
# class Person(db.Model):
#     __searchable__ = ['person_id', 'name']
#     generated_id = Column(Integer, primary_key=True)
#     person_id = Column(String)
#     roi = Column(Float)
#     name = Column(String)

# wa.whoosh_index(app, Person)  # pass in the class we want to index