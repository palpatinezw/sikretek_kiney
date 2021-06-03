from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User

class RegForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	description = StringField('Description', validators=[DataRequired()])

	def validate_username(self, username) :
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username is taken. Please choose a different username.')

	def validate_email(self, email) :
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('There is already an account with this email!')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember me!')
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')
	description = StringField('User Description', validators=[Length(min = 1, max = 300)])

	def validate_username(self, username) :
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username is taken. Please choose a different username.')

	def validate_email(self, email) :
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('There is already an account with this email!')

class WordForm(FlaskForm):
	sikret = StringField('Sikretek Kiney', validators=[DataRequired(), Length(min = 1, max = 50)])
	wordtype = StringField('Word Type', validators=[Length(max = 50)])
	definition = TextAreaField('Definition', validators=[Length(max = 200)])
	submit = SubmitField('Update')

class DeleteForm(FlaskForm):
	submit = SubmitField('Delete This Word')

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email) :
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('No account with this email! Please register an account first.')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')