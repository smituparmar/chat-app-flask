from flask_wtf import  FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextField,SelectField
from wtforms.validators import  InputRequired, Length, EqualTo

from models import User

def invalid_credentials(form,field):
	"""username and password checker"""
	username_entered=form.username.data
	password_entered=field.data

	user_object = User.query.filter_by(username=username_entered).first()
	if user_object is None:
			raise ValidationError("User or password is incorrect")

	elif password_entered!= user_object.password:
			raise ValidationError("User or password is incorrect")
	return

class RegistrationForm(FlaskForm):
	"""Registration form"""

	username = StringField("username_label",validators=[
		InputRequired(message="enter username"),
		Length(min=4,max=15,message="enter proper username")
		])

	password = PasswordField("password_label",validators=[
		InputRequired(message="enter password"),
		Length(min=4,max=15,message="enter proper password")])

	confirm_pswd = PasswordField("confirm_pswd_label",validators=[
		InputRequired(message="enter password"),
		EqualTo('password',message="password must match")])

	submit_button = SubmitField('Create')

class LoginForm(FlaskForm):
	"""Login Form"""
	username = StringField("username_label",validators=[
		InputRequired(message="enter username"),
		])

	password = PasswordField("password_label",validators=[
		InputRequired(message="enter password"),invalid_credentials])

	submit_button = SubmitField('Login')

class MessageScreen(FlaskForm):
	message= TextField("message")
	users=StringField("users")
	submit_button = SubmitField('send')

class CreateGroupScreen(FlaskForm):
	groupname = StringField('groupname')
	submit_button = SubmitField('create')

class GroupChat(FlaskForm):
	message= TextField("message")
	groupname=StringField("groupname")
	submit_button = SubmitField('send')

