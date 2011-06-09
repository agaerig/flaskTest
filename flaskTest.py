from contextlib import closing
import psycopg2
import sys
from flask import Flask
from flask import render_template, request, g, redirect, url_for, flash

#adding a comment for the purposes of testing git
#adding another comment for another test.

flaskTest = Flask(__name__)
flaskTest.secret_key = 'testkey'
conn_string = "host='localhost' dbname='flaskTest' user='NO USERNAME' password='NO PASSWORD'"
try:
	conn = psycopg2.connect(conn_string)
except:
	exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
	sys.exit("Database connection failed!\n ->%s" % (exceptionValue))
	
def init_db():
	with closing(connect_db()) as db:
		cursor = db.cursor()
		with flaskTest.open_resource('schema.sql') as f:
			cursor.execute(f.read())
		db.commit()
	
def connect_db():
	return psycopg2.connect(conn_string)
	
@flaskTest.before_request
def before_request():
	g.db = connect_db()
	
@flaskTest.after_request
def after_request(response):
	g.db.close()
	return response

@flaskTest.route('/')
@flaskTest.route('/index/')
def index():
	return render_template('index.html')

@flaskTest.route('/location/')
def location():
	return render_template('location.html')	
	
@flaskTest.route('/rsvp/', methods=['GET', 'POST'])
def rsvp():
	if request.method == 'POST':
		if request.form['rsvp'] == 'Yes':
			return render_template('accept.html')
		elif request.form['rsvp'] == 'No':
			return render_template('decline.html')
	else:
		return render_template('rsvp.html')
		
@flaskTest.route('/addAcceptance', methods=['GET','POST'])
def addAcceptance():
	if request.method == 'POST':
		errors = []
		if not request.form['name']:
			errors.append('You forgot to enter your name!')
			
		if not request.form.get("food"):
			errors.append('Please indicate your food choice.')
			
		if not request.form['email']:
			errors.append("Please give us your email so we can be in touch!")
			
		size = len(errors)
		if size > 0:
			return render_template('/accept.html',errors=errors)
		else:
			cursor = g.db.cursor()
			cursor.execute("""INSERT INTO accepts (name, email, phone, food, note) 
							VALUES (%s, %s, %s, %s, %s)""", (request.form['name'], request.form['email'], 
							request.form['phone'], request.form['food'], request.form['request']))
			g.db.commit()
			flash('New accept was successfully posted')
			return redirect(url_for('thanksPage'))
			
@flaskTest.route('/thanks/')
def thanksPage():
	return render_template('/thank-you.html')

@flaskTest.route('/addDecline', methods=['GET','POST'])
def addDecline():
	if request.method == 'POST':
		cursor = g.db.cursor()
		cursor.execute("""INSERT INTO decline (name, note) VALUES (%s, %s);""", 
						(request.form['name'], request.form['message']))
		g.db.commit()
		flash('New decline was successfully posted')
		return redirect(url_for('thanksPage'))
	else:
		return 'no post method'
		
@flaskTest.route('/registry/')
def registry():
	return render_template('registry.html')
	
@flaskTest.route('/accept', methods=['GET', 'POST'])
def accept():
	return render_template('accept.html')
	
@flaskTest.route('/decline')
def decline():
	return render_template('decline.html')

@flaskTest.route('/admin/')
@flaskTest.route('/admin')
def admin():
	return render_template('admin.html')
	
@flaskTest.route('/admin/accepts')
def adminAccepts():
	cursor = g.db.cursor()
	cursor.execute("""SELECT name, email, phone, food, note from accepts""")
	accepts = [dict(name = row[0], email = row[1], phone = row[2], food = row[3], request = row[4]) for row in cursor.fetchall()]
	return render_template('admin-accepts.html', accepts=accepts)
	
@flaskTest.route('/admin/decline')
def adminDecline():
	cursor = g.db.cursor()
	cursor.execute("""SELECT name, note from decline""")
	declines = [dict(name=row[0],message=row[1]) for row in cursor.fetchall()]
	return render_template('admin-decline.html', declines=declines)
	
if __name__ == '__main__':
	flaskTest.run(debug=True)