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

    @classmethod
    def find_by_username(self, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def current_user(self, session):
        return User.find_by_username(session['username'])

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
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    content = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<Answer %r>' % self.content


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        question_title = request.form['title']
        question_content = request.form['content']
        try:
            current_user_id = User.current_user(session).id
            new_question = Question(title=question_title, content=question_content, user_id=current_user_id)
            db.session.add(new_question)
            db.session.commit()
            return redirect('/')
        except:
            return "Your question could not be submitted. Sorry!"

    else:
        questions = Question.query.order_by(Question.created_on).all()
        return render_template('questions/index.html', questions = questions)

@app.route('/new')
def new_question():
    if 'username' not in session:
        return redirect('/login')
    else:
        return render_template('questions/new.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =="POST":
        claimed_username = request.form['username']
        claimed_password = request.form['password']
        claimed_user = User.find_by_username(claimed_username)
        if not claimed_user:
            return "Invalid username. Sorry!"
        else:
            if bcrypt.check_password_hash(claimed_user.password, claimed_password):
                session['username'] = claimed_user.username
                return redirect('/')
            else:
                return "User authentication failed. Sorry!"

    else:
        return render_template('users/login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        chosen_username = request.form['username']
        chosen_password = request.form['password']
        chosen_password_hash = bcrypt.generate_password_hash(chosen_password)
        new_user = User(username=chosen_username, password=chosen_password_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect('/')
        except:
            return "Account registration failed. Sorry!"

    else:
        return render_template('users/register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/questions/<int:question_id>')
def questions(question_id):
    question = Question.query.get(question_id)
    answers = question.answers
    return render_template('questions/show.html', question = question, answers = answers)


if __name__ == "__main__":
    app.run(debug=True)