from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Users/admin/desktop/programming/Project_1_Answer_System/Draft5/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializations
db = SQLAlchemy(app)
Bootstrap(app)

# Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)

# The below gives the page redirect if a non-logged in user tries to access a login restricted page. (so the below redirects to /login)
login_manager.login_view = 'login'

# Database Classes
# DB Classes for Question Related Stuff
class Subject(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(40), unique=True)
	# Back Reference
	blocks = db.relationship('Block', backref='subject', lazy='dynamic')
	#users = db.relationship('User', backref='subject', lazy='dynamic')
	units = db.relationship('Unit', backref='subject', lazy='dynamic')

	def __repr__(self):
		return '<Subject {}>'.format(self.title)

class Unit(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	title = db.Column(db.String(40))
	# Foreign Keys
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	# Back reference
	lessons = db.relationship('Lesson', backref='unit', lazy='dynamic')

	def __repr__(self):
		return '<Unit {}: {}>'.format(self.number, self.title)

class Lesson(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	title = db.Column(db.String(40))
	date_assigned = db.Column(db.DateTime)
	active = db.Column(db.Boolean)
	pdf_url = db.Column(db.String)
	# Foreign Keys
	unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
	# Back reference
	questions = db.relationship('Question', backref='lesson', lazy='dynamic')

	def __repr__(self):
		return '<Unit: {}, Lesson: {} - {}>'.format(self.unit.number, self.number, self.title)

class Question(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	html = db.Column(db.String)
	# Foreign Keys
	lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
	# Back reference
	parts = db.relationship('Part', backref='question', lazy='dynamic')

	def __repr__(self):
		return '<Unit: {}, Lesson: {}, Question: {}>'.format(self.lesson.unit.number, self.lesson.number, self.number)

class Part(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	letter = db.Column(db.String(1))
	html = db.Column(db.String)
	answer = db.Column(db.String)
	# Foreign Keys
	question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
	# Back reference
	responses = db.relationship('Response', backref='part', lazy='dynamic')

	def __repr__(self):
		return '<Unit: {}, Lesson: {}, Question: {}, Part: {}>'.format(self.question.lesson.unit.number, self.question.lesson.number, self.question.number, self.letter)

# DB Classes for Question Related Stuff
class Block(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	# Foreign Keys
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	# Back Reference
	users = db.relationship('User', backref='block', lazy='dynamic')

	def __repr__(self):
		return '<Subject: {}, Block: {}>'.format(self.subject.title, self.number)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	account_type = db.Column(db.String(20)) # either 'Student' or 'Teacher'
	first_name = db.Column(db.String(40))
	last_name = db.Column(db.String(40))
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	# Foreign Keys
	#subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	block_id = db.Column(db.Integer, db.ForeignKey('block.id'))
	# Back Reference
	responses = db.relationship('Response', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<Name: {} {}, Subject: {}>'.format(self.first_name, self.last_name, self.block.subject.title)

class Response(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	answer_text = db.Column(db.String(30))
	status = db.Column(db.Boolean)
	tries = db.Column(db.Integer)
	last_attempt_time = db.Column(db.DateTime)
	# Foreign Keys
	part_id = db.Column(db.Integer, db.ForeignKey('part.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<User: {} {}, {}, U{}-L{}-Q{}({})>'.format(self.user.first_name, self.user.last_name, 
			self.user.block.subject.title, self.part.question.lesson.unit.number, self.part.question.lesson.number,
			self.part.question.number, self.part.letter)

class UserView(ModelView):
	def on_model_change(self, form, model, is_created):
		model.password = generate_password_hash(model.password, method='sha256')

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(Subject, db.session))
admin.add_view(ModelView(Unit, db.session))
admin.add_view(ModelView(Lesson, db.session))
admin.add_view(ModelView(Question, db.session))
admin.add_view(ModelView(Part, db.session))
admin.add_view(ModelView(Block, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Response, db.session))

# Form Stuff
class LoginForm(FlaskForm):
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	
class SignUpForm(FlaskForm):
	first_name = StringField(label='First Name', validators=[InputRequired(), Length(max=40)])
	last_name = StringField(label='Last Name', validators=[InputRequired(), Length(max=40)])
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	subject = SelectField(label='Subject', validators=[InputRequired()], choices=[('alg2','Algebra 2 Common Core'), ('apcsp','AP Computer Science Principles')])
	block = SelectField(label='Block', validators=[InputRequired()], choices=[('1',1),('2',2),('3',3),('4',4),('5',5)])

class CreateUserForm(FlaskForm):
	first_name = StringField(label='First Name', validators=[InputRequired(), Length(max=40)])
	last_name = StringField(label='Last Name', validators=[InputRequired(), Length(max=40)])
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	subject = SelectField(label='Subject', validators=[InputRequired()], choices=[('alg2','Algebra 2 Common Core'), ('apcsp','AP Computer Science Principles')])
	subject = SelectField(label='Subject', validators=[InputRequired()], choices=[('alg2','Algebra 2 Common Core'), ('apcsp','AP Computer Science Principles')])
	block = SelectField(label='Block', validators=[InputRequired()], choices=[('1',1),('2',2),('3',3),('4',4),('5',5)])

class SelectStudentForm(FlaskForm):
	subjects = Subject.query.all()
	choices = [('','')]
	for subject in subjects:
		choices.append((subject.id,subject.title))
	subject = SelectField(label='Subject', choices=choices)
	unit = SelectField(label='Unit', choices=[])
	lesson = SelectField(label='Lesson', choices=[])
	block = SelectField(label='Block', choices=[])
	user = SelectField(label='User', choices=[])

# The route below is linked to when a user logs in. Searches the database by ID and gets user info
# After logging in the user, all user data from the User table should be accessible by using 'current_user.PROPERTY'.
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

# Student Pages
# Creating a new user:
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignUpForm()

	if form.validate_on_submit():
		if form.subject.data == 'alg2':
			subject_name = 'Algebra 2 Common Core'
		elif form.subject.data == 'apcsp':
			subject_name = 'AP Computer Science Principles'
		else: 
			return 'Error'

		subject = Subject.query.filter(Subject.title == subject_name).first()
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		block = Block.query.filter(Block.number == form.block.data).first()
		new_user = User(account_type='Student', first_name=form.first_name.data, last_name=form.last_name.data,
			email=form.email.data, password=hashed_password, block=block)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('dashboard'))

	return render_template('signup.html', form=form)

# Logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				# below logs in the user to the flask user extension
				login_user(user)
				# sends the logged in user to the dashboard
				return redirect(url_for('dashboard'))

	return render_template('login.html', form=form)

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
	if current_user.account_type == 'Admin':
		return render_template('admin_dashboard.html')
	else:
		subject = current_user.block.subject
		units = subject.units.all()
		return render_template('dashboard.html', units=units, subject_name=subject.title)

# Format url like /alg2/u2/l1
# Format url like /apcsp/...
@app.route('/assignment/<subject>/<unit>/<lesson>', methods=['GET', 'POST'])
@login_required
def assignment(subject, unit, lesson):
	if subject == 'alg2':
		subject_name = 'Algebra 2 Common Core'
	elif subject == 'apcsp':
		subject_name = 'AP Computer Science Principles'
	else: 
		return redirect(url_for('dashboard'))

	unit_number = int(unit[1:])
	lesson_number = int(lesson[1:])

	subject = Subject.query.filter(Subject.title == subject_name).first()
	unit = subject.units.filter(Unit.number == unit_number).first()
	lesson = unit.lessons.filter(Lesson.number == lesson_number).first()
	questions = lesson.questions.all()
	responses = Response.query.filter(Response.user_id == current_user.id).all()

	# I need to provide more error handling here - like what if student is messing around with url and unit/lesson do not exist?
	# Also need to block access for unit/lesson that are 'not available', so need to check if lesson is available before students allowed to access

	user_class = current_user.block.subject.title
	if user_class == subject_name:
		return render_template('assignment.html', questions=questions, unit=unit, lesson=lesson, responses=responses)
	else:
		return redirect(url_for('dashboard'))

@app.route('/check', methods=['POST'])
@login_required
def check():
	answer = request.form['answer']
	part_id = request.form['part_id']
	user_id = request.form['user_id']
	now = datetime.utcnow()

	part = Part.query.get(int(part_id))

	if answer == part.answer:
		correct = True
	else:
		correct = False

	response = Response.query.filter(Response.part_id == part.id).filter(Response.user_id == current_user.id).first()

	if response:
		response.answer_text = answer
		response.last_attempt_time = now
		response.status = correct
		response.tries += 1
	else:
		response = Response(answer_text=answer, status=correct, tries=1, last_attempt_time=now, part_id=part.id, user_id=current_user.id)
		db.session.add(response)

	db.session.commit()

	return jsonify({'correct' : correct})

@app.route('/test')
def test():
	return render_template('test.html', Subject=Subject, Block=Block, User=User)

@app.route('/test3', methods=['GET', 'POST'])
def test3():
	form = SelectStudentForm()

	if request.method == 'POST':
		return redirect(url_for('view_user_lesson', lesson_id=form.lesson.data, user_id=form.user.data))
		return '{} {} {}'.format(form.subject.data, form.block.data, form.user.data)

	return render_template('test3.html', form=form)

@app.route('/get_blocks', methods=['POST'])
def get_blocks():
	data = request.get_json()
	subject_id = int(data['subject_id'])
	form = SelectStudentForm()
	
	form.block.choices = block_query(subject_id)
	return str(form.block)

def block_query(subject_id):
	subject = Subject.query.get(subject_id)

	blocks = subject.blocks.all()
	block_choices = [('','')]
	for block in blocks:
		block_choices.append((block.id,block.number))
	return block_choices

@app.route('/get_users', methods=['POST'])
def get_users():
	data = request.get_json()
	block_id = int(data['block_id'])
	form = SelectStudentForm()
	
	form.user.choices = user_query(block_id)
	return str(form.user)

def user_query(block_id):
	block = Block.query.get(block_id)

	users = block.users.all()
	user_choices = [('','')]
	for user in users:
		user_choices.append((user.id,user.first_name + ' ' + user.last_name))
	return user_choices

@app.route('/get_units', methods=['POST'])
def get_units():
	data = request.get_json()
	subject_id = int(data['subject_id'])
	form = SelectStudentForm()
	
	form.unit.choices = unit_query(subject_id)
	return str(form.unit)

def unit_query(subject_id):
	subject = Subject.query.get(subject_id)

	units = subject.units.all()
	unit_choices = [('','')]
	for unit in units:
		unit_choices.append((unit.id,'U' + str(unit.number) + ': ' + unit.title))
	return unit_choices

@app.route('/get_lessons', methods=['POST'])
def get_lessons():
	data = request.get_json()
	unit_id = int(data['unit_id'])
	form = SelectStudentForm()
	
	form.lesson.choices = lesson_query(unit_id)
	return str(form.lesson)

def lesson_query(unit_id):
	unit = Unit.query.get(unit_id)

	lessons = unit.lessons.all()
	lesson_choices = [('','')]
	for lesson in lessons:
		lesson_choices.append((lesson.id,'U' + str(lesson.number) + ': ' + lesson.title))
	return lesson_choices




@app.route('/processjson', methods=['POST'])
def processjson():
	data = request.get_json()
	name = data['name']
	letters = list(name)
	return jsonify({"name" : name, "letters" : letters})


@app.route('/table')
def table():
	return render_template('table.html')

@app.route('/table2')
def table2():
	parts = Part.query.join(Question).join(Lesson).filter(Lesson.id == 1).all()
	parts = sorted(parts, key=lambda part: (part.question.lesson.unit.number, 
		part.question.lesson.number, part.question.number,
		part.letter))

	responses = Response.query.filter(Response.user_id == 2).join(Part).join(Question).join(Lesson).filter(Lesson.id == 1)
	# responses = sorted(responses, key=lambda response: (response.part.question.lesson.unit.number, 
		# response.part.question.lesson.number, response.part.question.number,
		# response.part.letter))

	user = User.query.get(2)
	user_data = {
			'first_name' : user.first_name,
			'last_name' : user.last_name
		}
	lesson = Lesson.query.get(1)
	lesson_data = {
			'unit_number' : lesson.unit.number,
			'lesson_number' : lesson.number,
			'lesson_title' : lesson.title
		}
	data = {'user_data' : user_data,
			'lesson_data' : lesson_data,
			'response_data' : []}
	for part in parts:
		response = Response.query.filter(Response.user_id == 2).join(Part).filter(Part.id == part.id).first()
		if response:
			if response.status:
				correct = '<span class="answer_reaction glyphicon glyphicon-ok" aria-hidden="true"></span>'
			else:
				correct = '<span class="answer_reaction glyphicon glyphicon-remove" aria-hidden="true"></span>'
			response_data = {
				'lesson' : response.part.question.lesson.number,	
				'question' : response.part.question.number,			
				'part' : response.part.letter,
				'last_try_date' : response.last_attempt_time,
				'tries' : response.tries,
				'correct' : correct
			}
		else:
			response_data = {
				'lesson' : part.question.lesson.number,	
				'question' : part.question.number,			
				'part' : part.letter,
				'last_try_date' : None,
				'tries' : None,
				'correct' : None
			}
		data['response_data'].append(response_data)
	# print(data)
	return render_template('table2.html', data=data)

@app.route('/table3', methods=['POST'])
def table3():
	# Json data that is sent has the form:
	# { 
	#	lesson_id : 1,
	#	user_id : 1
	# }
	if request.get_json():
		data = request.get_json()
		lesson_id = data['lesson_id']
		user_id = data['user_id']
	else:
		lesson_id = request.form['lesson']
		user_id = request.form['user']

	parts = Part.query.join(Question).join(Lesson).filter(Lesson.id == lesson_id).all()
	parts = sorted(parts, key=lambda part: (part.question.lesson.unit.number, 
		part.question.lesson.number, part.question.number,
		part.letter))

	responses = Response.query.filter(Response.user_id == user_id).join(Part).join(Question).join(Lesson).filter(Lesson.id == lesson_id)
	data = []
	for part in parts:
		response = Response.query.filter(Response.user_id == user_id).join(Part).filter(Part.id == part.id).first()
		if response:
			if response.status:
				correct = '<span class="answer_reaction glyphicon glyphicon-ok" aria-hidden="true"></span>'
			else:
				correct = '<span class="answer_reaction glyphicon glyphicon-remove" aria-hidden="true"></span>'
			response_data = {
				'lesson' : response.part.question.lesson.number,	
				'question' : response.part.question.number,			
				'part' : response.part.letter,
				'last_try_date' : response.last_attempt_time,
				'tries' : response.tries,
				'correct' : correct
			}
		else:
			response_data = {
				'lesson' : part.question.lesson.number,	
				'question' : part.question.number,			
				'part' : part.letter,
				'last_try_date' : None,
				'tries' : None,
				'correct' : None
			}
		data.append(response_data)
	return render_template('table2.html', data=data)

@app.route('/view_user_lesson/<lesson_id>/<user_id>')
def view_user_lesson(lesson_id, user_id):
	lesson_id = int(lesson_id)
	user_id = int(user_id)

	parts = Part.query.join(Question).join(Lesson).filter(Lesson.id == lesson_id).all()
	parts = sorted(parts, key=lambda part: (part.question.lesson.unit.number, 
		part.question.lesson.number, part.question.number,
		part.letter))

	user = User.query.get(user_id)
	user_data = {
			'first_name' : user.first_name,
			'last_name' : user.last_name
		}
	lesson = Lesson.query.get(lesson_id)
	lesson_data = {
			'unit_number' : lesson.unit.number,
			'lesson_number' : lesson.number,
			'lesson_title' : lesson.title
		}
	data = {'user_data' : user_data,
			'lesson_data' : lesson_data,
			'response_data' : []}

	responses = Response.query.filter(Response.user_id == user_id).join(Part).join(Question).join(Lesson).filter(Lesson.id == lesson_id)
	for part in parts:
		response = Response.query.filter(Response.user_id == user_id).join(Part).filter(Part.id == part.id).first()
		if response:
			if response.status:
				correct = '<span class="answer_reaction glyphicon glyphicon-ok" aria-hidden="true"></span>'
			else:
				correct = '<span class="answer_reaction glyphicon glyphicon-remove" aria-hidden="true"></span>'
			response_data = {
				'lesson' : response.part.question.lesson.number,	
				'question' : response.part.question.number,			
				'part' : response.part.letter,
				'last_try_date' : response.last_attempt_time,
				'tries' : response.tries,
				'correct' : correct
			}
		else:
			response_data = {
				'lesson' : part.question.lesson.number,	
				'question' : part.question.number,			
				'part' : part.letter,
				'last_try_date' : None,
				'tries' : None,
				'correct' : None
			}
		data['response_data'].append(response_data)
	return render_template('table2.html', data=data)

@app.route('/create_lesson', methods=['GET', 'POST'])
def create_lesson():
	if request.method == 'POST':

		question = Question(number=request.form["question_number"],html=request.form["question_html"],lesson=Lesson.query.get(int(request.form["lesson"])))
		db.session.add(question)
		db.session.commit()
		question_num = 1

		part_letters = request.form.getlist('part_letter')
		part_htmls = request.form.getlist('part_html')
		part_answers = request.form.getlist('part_answer')

		for part_letter, part_html, part_answer in zip(part_letters, part_htmls, part_answers):
			part = Part(letter=part_letter,html=part_html,answer=part_answer,question=question)
			db.session.add(part)

		db.session.commit()


	subject = Subject.query.all()
	unit = Unit.query.all()
	lesson = Lesson.query.all()
	return render_template('create_lesson.html', subjects=subject, units=unit, lessons=lesson)

@app.route('/logout')
@login_required
def logout():
	logout_user() # this is a method that was imported from Flask-Login
	return redirect(url_for('login'))


if __name__ == "__main__":
	app.run(debug=True)