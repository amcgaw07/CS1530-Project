from flask import Flask, render_template,session, url_for, redirect, abort, g, flash, _app_ctx_stack, request
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from datetime import date
import time
import os
from hashlib import md5
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Admin, User
import tmdbsimple as tmbd
import json
tmbd.API_KEY='9d442b83bb8972605022892d3c12fb0e'
app = Flask(__name__)
# configuration
PER_PAGE = 30
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'users.db')

app.config.from_object(__name__)
app.config.from_envvar('USER_SETTINGS', silent=True)

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	admin_user = Admin(username="admin", password="pass")
	db.session.add(admin_user)
	db.session.commit()
	print('Initialized the database.')

def get_admin_id(username):
	"""Convenience method to look up the id for a username."""
	rv = Admin.query.filter_by(username=username).first()
	return rv.admin_id if rv else None

def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

@app.before_request
def before_request():
	g.user = None
	g.admin = None
	if 'admin_id' in session:
		g.admin = Admin.query.filter_by(admin_id=session['admin_id']).first()
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()
	


# Register a user
@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the customer."""
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_admin_id(request.form['username']) is not None:
			error = 'The username is already taken'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(username=request.form['username'], password=request.form['password']))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('index.html', error=error)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	error = None
	if request.method == 'POST':
		if not Admin.query.filter_by(username=request.form['username'], password=request.form['password']).first() is None:
			session['admin_id'] = admin.query.filter_by(username=request.form['username']).first().admin_id
			flash('You were logged in')
			return redirect(url_for('admin'))
		elif not User.query.filter_by(username=request.form['username'], password=request.form['password']).first() is None:
			session['user_id'] = User.query.filter_by(username=request.form['username']).first().user_id
			flash('You were logged in')
			return redirect(url_for('index', username=request.form['username'], password=request.form['password']))
		else:
			error = 'Invalid username or password'
	return render_template("index.html", error=error)
@app.route('/logoutUser')
def logoutUser():
	"""Logs the user member out."""
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('login'))

@app.route('/logoutAdmin')
def logoutAdmin():
	"""Logs the admin out."""
	flash('You were logged out')
	session.pop('admin_id', None)
	return redirect(url_for('login'))



@app.route('/')
@app.route('/index.html')
def index():
        import requests
        
        search = tmbd.Movies(603)
        response1 = search.info()
        
        imdb_id = '603'
        url = 'https://api.themoviedb.org/3/movie/'+imdb_id+'/watch/providers?api_key=9d442b83bb8972605022892d3c12fb0e'
        response = requests.get(url)
        test = json.loads(response.text)


        
        return render_template('index.html', the_title='where movie', response= test['results']['US'])


@app.route('/symbol.html')
def symbol():
    return render_template('symbol.html', the_title='Tiger As Symbol')

@app.route('/myth.html')
def myth():
    return render_template('myth.html', the_title='Tiger in Myth and Legend')

if __name__ == '__main__':
    app.run(debug=True)
