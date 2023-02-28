from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite3:///development.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True)
    questions = db.relationship('Question', backref = 'user')
    answers = db.relationship('Answer', backref = 'user')
    date_created = db.Column(db.DateTime)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey(users.id))
    title = db.Column(db.String)
    content = db.Column(db.String)
    date_created = db.Column(db.DateTime)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey(users.id))
    title = db.Column(db.String)
    content = db.Column(db.String)
    date_created = db.Column(db.DateTime)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)