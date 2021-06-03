from flask import render_template, request, url_for, flash, redirect, abort
from main import app, db, bcrypt, mail
from main.models import User, Word
from main.forms import RegForm, LoginForm, UpdateAccountForm, WordForm, DeleteForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
import logging
from flask_mail import Message

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dictionary")
def dictionary():
	page = request.args.get('page', 1, type=int)
	fullword = Word.query.order_by(Word.sikret.asc()).paginate(page=page, per_page=12)
	words = [[],[],[],[]]
	i = 0
	for k in range(4):
		for j in range(3):
			if i >= len(fullword.items):
				words[k].append(Word(sikret='', definition='', wordtype=''))
				continue
			words[k].append(fullword.items[i])
			i = i+1
		if i >= len(fullword.items):
			break
	return render_template("dictionary.html", title='Dictionary', words=words, fullwords=fullword)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegForm()
	if form.validate_on_submit():
		hpw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email=form.email.data, password=hpw, description=form.description.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created! You may now login.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			flash(f'{form.username.data} logged in!', 'success')
			return redirect(url_for('home'))
		else:
			flash(f'Login failed!', 'error')
	return render_template('login.html', title='Login', form=form)

def save_picture(form_picture) :
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', fn)
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.crop((0, 0, 125, 125))
	i.save(picture_path)
	return fn

@app.route("/user")
@login_required
def user():
	# form = UpdateAccountForm()
	# if form.validate_on_submit():
	# 	if form.picture.data:
	# 		pf = save_picture(form.picture.data)
	# 		current_user.image_file = pf
	# 	current_user.username = form.username.data
	# 	current_user.email = form.email.data
	# 	db.session.commit()
	# 	flash('Update succesful!', 'success')
	# 	return redirect(url_for('user'))
	# elif request.method == 'GET':
	# 	form.username.data = current_user.username
	# 	form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('user.html', title='Account', img_file = image_file)

@app.route("/edituser", methods=['GET', 'POST'])
@login_required
def edituser():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			pf = save_picture(form.picture.data)
			current_user.image_file = pf
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.description = form.description.data
		db.session.commit()
		flash('Update succesful!', 'success')
		return redirect(url_for('user'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.description.data = current_user.description
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('useredit.html', title='Account', img_file = image_file, form =  form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash(f'Logout successful!', 'success')
	return redirect(url_for('home'))

@app.route("/word/new", methods=['GET', 'POST'])
@login_required
def new_word():
	if current_user.admin < 1:
		abort(403)
	form = WordForm()
	if form.validate_on_submit():
		word = Word(sikret=form.sikret.data, definition=form.definition.data, wordtype=form.wordtype.data)
		db.session.add(word)
		db.session.commit()
		flash('Word Added', 'success')
		return redirect(url_for('home'))
	return render_template('wordmodifier.html', title='Word creation', form=form, legend='New Word')

@app.route("/word/<int:word_id>")
def word(word_id):
	word = Word.query.get_or_404(word_id)
	return render_template('word.html', title=word.sikret, word=word)

@app.route("/word/<int:word_id>/update", methods=['GET', 'POST'])
@login_required
def update_word(word_id):
	if current_user.admin < 1:
		abort(403)
	word = Word.query.get_or_404(word_id)
	form = WordForm()
	if form.validate_on_submit():
		word.sikret = form.sikret.data
		word.definition = form.definition.data
		word.wordtype = form.wordtype.data
		db.session.commit()
		flash('Update successful', 'success')
		return redirect(url_for('word', word_id = word.id))
	elif request.method == 'GET':
		form.sikret.data = word.sikret
		form.definition.data = word.definition
		form.wordtype.data = word.wordtype
	return render_template('wordmodifier.html', title='Word Update', form=form, legend='Update Post')

@app.route("/word/<int:word_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_word(word_id):
	if current_user.admin < 1:
		abort(403)
	form = DeleteForm()
	word = Word.query.get_or_404(word_id)
	if form.validate_on_submit():
		db.session.delete(word)
		db.session.commit()
		flash('Word deleted!', 'success')
		return redirect(url_for('home'))
	return render_template('deleteword.html', title='Delete Word', form = form, word=word)

@app.route("/user/<string:username>")
def user_info(username):
	user = User.query.filter_by(username=username).first_or_404()
	image_file = url_for('static', filename='profile_pics/' + user.image_file)
	return render_template('userinfo.html', title=username, user=user, img_file=image_file)

@app.route("/user/<string:username>/admin")
@login_required
def admin(username):
	if current_user.admin < 1:
		abort(403)
	user = User.query.filter_by(username=username).first_or_404()
	user.admin = 1
	db.session.commit()
	flash(f'{username} is now an admin!', 'success')
	return redirect(url_for('user_info', username=username))

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='octaviusfc@gmail.com', recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_pw', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made. 
'''
	mail.send(msg)
	


@app.route("/resetpassword", methods=['GET', 'POST'])
def reset_req():
	if current_user.is_authenticated:
		return redirect(url_for('user'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('Password reset email sent!', 'success')
		return redirect(url_for('login'))

	return render_template('reset_req.html', title = 'Reset Password', form=form)

@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
def reset_pw(token):
	if current_user.is_authenticated:
		return redirect(url_for('user'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('This is an invalid or expired token!', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hpw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hpw
		db.session.commit()
		flash(f'Your password has been changed! You may now login.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_pw.html', title = 'Reset Password', form = form)