from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    time_limit = db.Column(db.Integer)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer)
    question = db.Column(db.String(200))
    o1 = db.Column(db.String(100))
    o2 = db.Column(db.String(100))
    o3 = db.Column(db.String(100))
    o4 = db.Column(db.String(100))
    answer = db.Column(db.String(100))

# ---------------- INIT ----------------

@app.before_first_request
def create_tables():
    db.create_all()

    if not User.query.filter_by(username="teacher").first():
        db.session.add(User(username="teacher", password="123", role="teacher"))
        db.session.add(User(username="student", password="123", role="student"))
        db.session.commit()

# ---------------- LOGIN ----------------

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(
        username=request.form['username'],
        password=request.form['password']
    ).first()

    if user:
        session['role'] = user.role
        return redirect('/teacher' if user.role == "teacher" else '/student')

    return "Invalid login"

# ---------------- TEACHER ----------------

@app.route('/teacher')
def teacher():
    tests = Test.query.all()
    return render_template("teacher.html", tests=tests)

@app.route('/create_test', methods=['POST'])
def create_test():
    test = Test(
        title=request.form['title'],
        time_limit=request.form['time']
    )
    db.session.add(test)
    db.session.commit()
    return redirect('/teacher')

@app.route('/add_question/<int:test_id>', methods=['POST'])
def add_question(test_id):
    q = Question(
        test_id=test_id,
        question=request.form['question'],
        o1=request.form['o1'],
        o2=request.form['o2'],
        o3=request.form['o3'],
        o4=request.form['o4'],
        answer=request.form['answer']
    )
    db.session.add(q)
    db.session.commit()
    return redirect('/teacher')

# ---------------- STUDENT ----------------

@app.route('/student')
def student():
    tests = Test.query.all()
    return render_template("student.html", tests=tests)

@app.route('/test/<int:test_id>')
def take_test(test_id):
    questions = Question.query.filter_by(test_id=test_id).all()
    test = Test.query.get(test_id)
    return render_template("test.html", questions=questions, test=test)

@app.route('/submit/<int:test_id>', methods=['POST'])
def submit(test_id):
    questions = Question.query.filter_by(test_id=test_id).all()
    score = 0

    for q in questions:
        if request.form.get(str(q.id)) == q.answer:
            score += 1

    return render_template("result.html", score=score, total=len(questions))

if __name__ == "__main__":
    app.run()