from main import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.png')
	password = db.Column(db.String(60), nullable = False)
	progress = db.Column(db.Integer, nullable=False, default=1)
	admin = db.Column(db.Integer, nullable=False, default=0)
	description = db.Column(db.String(300), default='Hello! I am learning Skrattain')

	def get_reset_token(self, expire_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expire_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def ver_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.admin}', '{self.description}')"

class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sikret = db.Column(db.String(50), nullable=False)
	definition = db.Column(db.String(200))
	wordtype = db.Column(db.String(50), nullable=False)

	def __repr__(self):
		return f"Word('{self.sikret}', '{self.wordtype}', '{self.definition}')"