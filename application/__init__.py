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

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route('/directorsearch', methods=['GET', 'POST'])
def directorsearch():
    # director = Person.query.whoosh_search(request.form.get("director")).all()[0]
    search_name = request.form.get("director").strip()
    print(search_name)
    c.execute('''SELECT name, person_id FROM PERSON WHERE name LIKE ?''', [search_name])
    director = c.fetchall()[0]
    print(director)
    directors.append(director)
    return render_template("index.html", directors=directors, writers=writers)


@app.route('/writersearch', methods=['GET', 'POST'])
def writersearch():
    # writer = Person.query.whoosh_search(request.form.get("writer")).all()[0]
    # TODO save the writer for later classify
    search_name = request.form.get("writer")
    director = c.execute('''SELECT name, person_id FROM PERSON WHERE name LIKE ?''', [search_name])[0]
    writers.append(writer)
    return render_template("index.html", directors=directors, writers=writers)


@app.route("/movieclassify", methods=['GET', 'POST'])
def movieclassify():

    # extract form inputs 
    plot = request.form.get("plot")
    
    #url for irisservice
    #url = "http://localhost:5000/api"
    url = "https://irismodel-app.herokuapp.com/api"

    #create json from form inputs
    data = json.dumps({"plot": plot, "director": directors, "writer": writers})

    #post json to url
    results =  requests.post(url,data)
    
    #send features and prediction result to index.html for display
    return render_template("index.html", plot = plot, director = director, writer = writer, results=results.content.decode('UTF-8'))


# # database models
# class Person(db.Model):
#     __searchable__ = ['person_id', 'name']
#     generated_id = Column(Integer, primary_key=True)
#     person_id = Column(String)
#     roi = Column(Float)
#     name = Column(String)

# wa.whoosh_index(app, Person)  # pass in the class we want to index