from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db= SQLAlchemy()

class User(UserMixin,db.Model):
	"""User model"""
	__tablename__ = "users"
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(25),unique=True,nullable=False)
	password = db.Column(db.String(),nullable=False)

class Messages(UserMixin,db.Model):
	__tablename__ = "messages"
	id = db.Column(db.Integer,primary_key=True)
	sender_id = db.Column(db.String(),nullable=False)
	receiver_id = db.Column(db.String(),nullable=False)
	message = db.Column(db.String(),nullable=False)
	time =db.Column(db.DateTime(),nullable=False)

class Group(UserMixin,db.Model):
	__tablename__ = "groups"
	id=db.Column(db.Integer,primary_key=True)
	groupname = db.Column(db.String(),unique=True,nullable=False)

class GroupMessages(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	sender_id = db.Column(db.String(),nullable=False)
	msg = db.Column(db.String(),nullable=False)

	def changeTableName(name):
		self.query=self.query.replace('group_messages',name)







	




	 
