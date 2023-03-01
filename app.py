from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///development.db'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.secret_key = 'THIS_KEY_FOR_DEVELOPMENT_USE_ONLY'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True)
    password = db.Column(db.String(80))
    questions = db.relationship('Question', backref = 'user')
    answers = db.relationship('Answer', backref = 'user')
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self) -> str:
        return '<User %r>' % self.username

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String)
    content = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<Question %r>' % self.title

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<Answer %r>' % self.content


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        question_title = request.form['title']
        if 'username' in session:
            new_question = Question(title=question_title, user_id=session['user_id'])
            try:
                db.session.add(new_question)
                db.session.commit()
                return redirect('/')
            except:
                return "Your question could not be submitted. Sorry!"
        
        else:
            return redirect('/login')

    else:
        questions = Question.query.order_by(Question.created_on).all()
        return render_template('questions/index.html', questions = questions)

@app.route('/new')
def new_question():
    return render_template('questions/new.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =="POST":
        claimed_username = request.form['username']
        claimed_password = request.form['password']
        claimed_user = User.query.filter_by(username=claimed_username).first()
        if bcrypt.check_password_hash(claimed_user.password, claimed_password):
            session['username'] = claimed_user.username
            session['user_id'] = claimed_user.id
            return redirect ('/')
        else:
            return "User authentication failed. Sorry!"

    else:
        return render_template('users/login.html')

@app.route('/register')
def register():
    if request.method == "POST":
        chosen_username = request.form['username']
        chosen_password = request.form['password']
        chosen_password_hash = bcrypt.generate_password_hash(chosen_password)
        new_user = User(username=chosen_username, password=chosen_password_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return "Account registration failed. Sorry!"

    else:
        return render_template('users/register.html')



if __name__ == "__main__":
    app.run(debug=True)