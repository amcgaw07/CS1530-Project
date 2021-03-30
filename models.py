from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from datetime import date
 
db = SQLAlchemy()

class Admin(db.Model):
	__tablename__ = 'admin'
	admin_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)
	password = db.Column(db.String(30), unique=True)
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
	
	def __repr__(self):
		return '<Admin {}>'.format(self.username)
		
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