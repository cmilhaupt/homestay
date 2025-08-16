from flask_login import UserMixin
from ..database import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    welcome_template = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
