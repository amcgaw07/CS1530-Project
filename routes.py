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
from models import db, User, Favorite, Subscription
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

#3 popular movies
url = "https://api.themoviedb.org/3/movie/popular?api_key=9d442b83bb8972605022892d3c12fb0e&language=en-US&page=1"
response = requests.get(url)
popularMovies = json.loads(response.text)

popular1 = ["https://image.tmdb.org/t/p/original/" + popularMovies['results'][0]['poster_path'], popularMovies['results'][0]['original_title'], popularMovies['results'][0]['overview']]
popular2 = ["https://image.tmdb.org/t/p/original/" + popularMovies['results'][1]['poster_path'], popularMovies['results'][1]['original_title'], popularMovies['results'][1]['overview']]
popular3 = ["https://image.tmdb.org/t/p/original/" + popularMovies['results'][2]['poster_path'], popularMovies['results'][2]['original_title'], popularMovies['results'][2]['overview']]


db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

@app.before_request
def before_request():
	g.user = None
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
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(username=request.form['username'], password=generate_password_hash(request.form['password'])))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login', error=error))
	return redirect(url_for('index', error=error))#render_template('index.html', error=error, movie1=popular1, movie2=popular2, movie3=popular3)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	error = None
	if request.method == 'POST':
		if not User.query.filter_by(username=request.form['username']).first() is None:
			user = User.query.filter_by(username=request.form['username']).first()
			if check_password_hash(user.password, request.form['password']):
				session['user_id'] = User.query.filter_by(username=request.form['username']).first().user_id
				flash('You were logged in')
				return redirect(url_for('index', error=error))
		else:
			error = 'Invalid username or password'
	return redirect(url_for('index', error=error))#render_template("index.html", error=error, movie1=popular1, movie2=popular2, movie3=popular3)
	
# User account page
@app.route('/accountPage', methods=['GET', 'POST'])
def accountPage():
	error = None
	user = User.query.filter_by(username=g.user.username).first()
	if request.method == 'POST':
		if not request.form['subscription']:
			error = 'You have to enter a streaming subscription'
		else:
			service = request.form['subscription']
			if Subscription.query.filter_by(user_id=user.user_id, subscription=service).first():
				error="You already added that streamings service to your subscriptions."
			else:
				db.session.add(Subscription(user_id=user.user_id, subscription=service))
				db.session.commit()
	favorites = Favorite.query.filter_by(user_id=user.user_id).all()
	subscriptions = Subscription.query.filter_by(user_id=user.user_id).all()
	favorites = sorted(favorites, key=lambda favorite: favorite.movie)
	subscriptions = sorted(subscriptions, key=lambda subscription: subscription.subscription)
	onAccount=True
	return render_template('accountPage.html', favorites=favorites, subscriptions=subscriptions, error=error)


@app.route('/favorite/<movie>', methods=['GET', 'POST'])
def favorite(movie):
	user = User.query.filter_by(username=g.user.username).first()
	db.session.add(Favorite(user_id=user.user_id, movie=movie))
	db.session.commit()
	return redirect(url_for('accountPage'))

@app.route('/unfavorite/<movie>', methods=['GET', 'POST'])
def unfavorite(movie):
	user = User.query.filter_by(username=g.user.username).first()
	db.session.delete(Favorite.query.filter_by(user_id=user.user_id, movie=movie).first())
	db.session.commit()
	return redirect(url_for('accountPage'))
	

@app.route('/favoriteSearch/<movie>/<movie_id>', methods=['GET', 'POST'])
def favoriteSearch(movie, movie_id):
	user = User.query.filter_by(username=g.user.username).first()
	db.session.add(Favorite(user_id=user.user_id, movie=movie))
	db.session.commit()
	return redirect(url_for('movieTest', movieId=movie_id, movieTitle=movie))

@app.route('/unfavoriteSearch/<movie>/<movie_id>', methods=['GET', 'POST'])
def unfavoriteSearch(movie, movie_id):
	user = User.query.filter_by(username=g.user.username).first()
	db.session.delete(Favorite.query.filter_by(user_id=user.user_id, movie=movie).first())
	db.session.commit()
	return redirect(url_for('movieTest', movieId=movie_id, movieTitle=movie))

@app.route('/cancel_subscription/<service>', methods=['GET', 'POST'])
def cancel_subscription(service):
	user = User.query.filter_by(username=g.user.username).first()
	db.session.delete(Subscription.query.filter_by(user_id=user.user_id, subscription=service).first())
	db.session.commit()
	return redirect(url_for('accountPage'))
	
@app.route('/logoutUser')
def logoutUser():
	"""Logs the user member out."""
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('login'))

@app.route('/')
def indexDefault():

	return render_template('index.html', the_title='Where\'s my Movie?', movie1=popular1, movie2=popular2, movie3=popular3)

@app.route('/index.html/<error>',methods=['GET','POST'])
def index(error):
	print(error)
	return render_template('index.html', the_title='Where\'s my Movie?', error=error, movie1=popular1, movie2=popular2, movie3=popular3)

@app.route('/movie', methods=['GET','POST'])
def movie():
    if request.method == "POST":
    	movieTitle = request.form['movieTitle']
    
    	url = "https://api.themoviedb.org/3/search/movie?api_key=9d442b83bb8972605022892d3c12fb0e&language=en-US&query="+movieTitle+"&page=1&include_adult=false"
    	response = requests.get(url)
    	test = json.loads(response.text)
    
    	#imdb_id = '603'
    	#url = 'https://api.themoviedb.org/3/movie/'+imdb_id+'/watch/providers?api_key=9d442b83bb8972605022892d3c12fb0e'
    	#response = requests.get(url)
    	#test = json.loads(response.text)
    	return render_template('movie.html', the_title=movieTitle, response = test['results'])

@app.route('/movieTest/<movieTitle>/<movieId>', methods=['GET','POST'])
def movieTest(movieId,movieTitle):
	import requests
	url = 'https://api.themoviedb.org/3/movie/'+movieId+'/watch/providers?api_key=9d442b83bb8972605022892d3c12fb0e'
	response = requests.get(url)
	test = json.loads(response.text)
	#pass in general movie info
	url_movie_info = "https://api.themoviedb.org/3/movie/" + movieId + "?api_key=9d442b83bb8972605022892d3c12fb0e&language=en-USh"
	response_movie_info = requests.get(url_movie_info)
	movie_info = json.loads(response_movie_info.text)

	url_movie_reviews = "https://api.themoviedb.org/3/movie/"+movieId+"/reviews?api_key=9d442b83bb8972605022892d3c12fb0e&language=en-US&page=1"
	reponse_movie_review = requests.get(url_movie_reviews)
	movie_reviews = json.loads(reponse_movie_review.text)
	
	isFavorite=False
	if (g.user is not None):
		user = User.query.filter_by(username=g.user.username).first()
		movie = Favorite.query.filter_by(user_id=user.user_id, movie=movieTitle).first()
		if (movie is None):
			isFavorite=False
		else:
			isFavorite=True
			print(isFavorite)

	return render_template('movie.html', the_title=movieTitle, id=movieId, response = test['results']['US'],  response2 = movie_info, reviews = movie_reviews, isFavorite=isFavorite)

@app.route('/symbol.html')
def symbol():
    return render_template('symbol.html', the_title='Tiger As Symbol')

@app.route('/myth.html')
def myth():
    return render_template('myth.html', the_title='Tiger in Myth and Legend')

if __name__ == '__main__':
    app.run(debug=True)