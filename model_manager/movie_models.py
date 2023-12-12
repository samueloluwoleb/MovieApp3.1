from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# create the extension
db = SQLAlchemy()


class Movies(db.Model):
    """
        Defines the class that represents the movies table in the database plus the
        instance variables which represent each table columns
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=False, unique=True)
    rating = db.Column(db.Float)
    director = db.Column(db.String)
    year = db.Column(db.String)


class Users(db.Model, UserMixin):
    """
        Defines the class that represents the users table in the database plus the
        instance variables which represent each table columns and methods to
        change state of data
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_h = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)

    def set_password(self, password):
        self.password_h = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_h, password)

    def is_authenticated(self):
        return True


class User_movies(db.Model):
    """
        Defines the class that represents the user_movies table in the database plus the
        instance variables which represent each table columns
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=False)
    rating = db.Column(db.String)
    director = db.Column(db.String)
    year = db.Column(db.String)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)


class Reviews(db.Model):
    """
        Defines the class that represents the reviews table in the database plus the
        instance variables which represent each table columns
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String)
    rating = db.Column(db.Float)


class Genres(db.Model):
    """
        Defines the class that represents the genres table in the database plus the
        instance variables which represent each table columns
    """
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
