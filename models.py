from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from datetime import date
 
db = SQLAlchemy()
		
class User(db.Model):
	__tablename__ = 'user'
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)
	password = db.Column(db.String(30))
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
	
	def __repr__(self):
		return '<User {}>'.format(self.username)
		
class Favorite(db.Model):
	__tablename__ = 'favorite'
	favorite_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	movie = db.Column(db.Text, nullable=False)
	
	def __init__(self, user_id, movie):
		self.user_id = user_id
		self.movie = movie
	
	def __repr__(self):
		return '<Movie {}>'.format(self.movie)
	
class Subscription(db.Model):
	__tablename__ = 'subscription'
	subscription_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	subscription = db.Column(db.Text, nullable=False)
	
	def __init__(self, user_id, subscription):
		self.user_id = user_id
		self.subscription = subscription
	
	def __repr__(self):
		return '<Subscription {}>'.format(self.subscription)
		
		