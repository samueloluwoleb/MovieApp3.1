import sqlalchemy
import requests
from urllib3.exceptions import ConnectTimeoutError
from datamanager.data_manager_interface import DataManagerInterface
from storage import genres_data
from model_manager.movie_models import *

API_KEY_MOVIES = '1081add1'


class SQLiteDataManager(DataManagerInterface):

    def get_user_movies(self, user_id):
        """
            performs read operation on user_movies tables and formats the data to return a list of movies
        :param user_id:
        :return:
        """
        try:
            movies = []
            movie_records = db.session.query(User_movies).filter(User_movies.user_id == user_id).all()
            for record in movie_records:
                movie_id = record.movie_id
                title = record.title.strip()
                director = record.director
                year = record.year
                rating = record.rating
                genre_id = record.genre_id
                movie = {"id": movie_id, "name": title, "director": director, "year": year,
                         "rating": rating, "genre_id": genre_id}
                movies.append(movie)
            return movies
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    def get_all_users(self):
        """
            performs read operation on users table and formats the data to return a list of dictionaries
            which contains all user details
        :return:
        """
        try:
            all_users = []
            all_users_details = self.get_all_userid_and_username()
            for userid_and_username in all_users_details:
                movies = self.get_user_movies(int(userid_and_username))
                all_users_details[userid_and_username]["movies"] = movies
            all_users.append(all_users_details)
            return all_users
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def create_genre_record():
        """
            performs create operation to creates all the records for the genres table
        :return:
        """
        try:
            data_genres = genres_data.GENRE_DATA
            for data in data_genres:
                new_entry = Genres(**data)
                db.session.add(new_entry)
            db.session.commit()
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def add_user(username, email, password, gender):
        """
            performs create operation on users table
        :param username:
        :param email:
        :param password:
        :param gender:
        :return:
        """
        try:
            user = Users(
                id=None,
                username=username,
                email=email,
                gender=gender
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_movie_info_api(searched_movie_param):
        """
            Searches the web through an api for more details about a searched movie and manipulate the response
            accordingly
        :param searched_movie_param:
        :return:
        """
        try:
            search_title = searched_movie_param
            url = f"https://www.omdbapi.com/?apikey={API_KEY_MOVIES}&t={search_title}"
            response = requests.get(url)
            response = response.json()

            # check if no movie match is found from omdbapi and return None for all fields
            if response['Response'] == 'False' and response['Error'] == 'Movie not found!':
                return None, None, None, None
            else:
                # Get the data from response if a match id found from omdbapi
                title = response.get('Title')
                director = response.get('Director')
                year = response.get('Year')
                rating = response.get('imdbRating')

                return title, rating, director, year

        except (AttributeError, ValueError, TypeError, ConnectionError, ConnectTimeoutError,
                requests.exceptions.ConnectTimeout):
            return None, None, None, None

    @staticmethod
    def get_movies_record(title):
        """
            performs read operation on movies table and returns values of specified columns
        :param title:
        :return:
        """
        try:
            movie_record = db.session.query(Movies).filter(Movies.title == title).one()
            return movie_record.id, movie_record.title, movie_record.rating, movie_record.director, movie_record.year
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def add_movies_record(title, rating, director, year):
        """
            performs create operation on movies table to create a record
        :param title:
        :param rating:
        :param director:
        :param year:
        :return:
        """
        try:
            movie = Movies(
                id=None,
                title=title,
                rating=rating,
                director=director,
                year=year
            )
            db.session.add(movie)
            db.session.commit()
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def add_user_movies_record(title, rating, director, year, genre_id, user_id, movie_id):
        """
            performs create operation on user_movies table to add a record
        :param title:
        :param rating:
        :param director:
        :param year:
        :param genre_id:
        :param user_id:
        :param movie_id:
        :return:
        """
        try:
            user_movie = User_movies(
                id=None,
                title=title,
                rating=rating,
                director=director,
                year=year,
                genre_id=genre_id,
                user_id=user_id,
                movie_id=movie_id

            )
            db.session.add(user_movie)
            db.session.commit()
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_user_movie_title(user_id, title):
        try:
            user_movie_title = db.session.query(User_movies.title) \
                .filter(User_movies.title == title, User_movies.user_id == user_id).one()
            return user_movie_title.title
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_user_movies_titles(user_id):
        try:
            titles_list = []
            user_movies_titles = db.session.query(User_movies.title).filter(User_movies.user_id == user_id).all()
            for movie_title in user_movies_titles:
                titles_list.append(movie_title.title)
            return titles_list
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_all_movies_title(title):
        """
            performs read operation on movies table to return a movie title based on specified condition
        :param title:
        :return:
        """
        try:
            movie_title = db.session.query(Movies.title).filter(Movies.title == title).one()
            return movie_title.title
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    def add_movie(self, title, rating, director, year, genre_id, user_id):
        """
            performs both get and create operations on movies and user_movies tables to create appropriate records
        :param title:
        :param rating:
        :param director:
        :param year:
        :param genre_id:
        :param user_id:
        :return:
        """
        try:
            user_movie_title = self.get_user_movie_title(user_id, title)
            if user_movie_title:
                return f"The movie: {title} - already exists in your catalogue"
            else:
                movie_title = self.get_all_movies_title(title)
                if movie_title:
                    movie_id, title, rating, director, year = self.get_movies_record(title)
                    self.add_user_movies_record(title, rating, director, year, genre_id, user_id, movie_id)
                    return f"Movie -- {title} -- successfully added"
                else:
                    self.add_movies_record(title, rating, director, year)
                    movie_id, title, rating, director, year = self.get_movies_record(title)
                    self.add_user_movies_record(title, rating, director, year, genre_id, user_id, movie_id)
                    return f"Movie -- {title} -- successfully added"
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_all_userid_and_username():
        """
            performs read operation on users table to return a dictionary of user_ids and usernames
            of all users
        :return:
        """
        try:
            userid_and_username_dict = {}
            all_userid_and_username = db.session.query(Users.id, Users.username).all()
            for userid_and_username in all_userid_and_username:
                user_id = str(userid_and_username.id)
                username = userid_and_username.username
                userid_and_username_dict[user_id] = {"name": username}
            return userid_and_username_dict
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_userid_password(email):
        """
            performs read operation on users table to return a dictionary of user_ids and usernames
            of all users
        :return:
        """
        user_info = {}
        try:
            user_details = db.session.query(Users).filter(Users.email == email).one()
            userid = user_details.id
            username = user_details.username
            password = user_details.password_h

            user_info["userid"] = userid
            user_info["username"] = username
            user_info["password"] = password

            return user_info

        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def verify_user_password(email, password):
        try:
            user = db.session.query(Users).filter(Users.email == email).one()

            if user and user.check_password(password):
                return True  # Password is correct
            else:
                return False  # Password is incorrect
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_user_name(user_id):
        """
            performs a read operation on users table to return a username that satisfy the queried conditions
        :param user_id:
        :return:
        """
        try:
            user_row = db.session.query(Users.username).filter(Users.id == user_id).one()
            user_name = user_row.username
            return user_name
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def add_user_review(movie_id, user_id, description, rating):
        """
            performs create operation on reviews table to add a record
        :param movie_id:
        :param user_id:
        :param description:
        :param rating:
        :return:
        """
        try:
            review = Reviews(
                id=None,
                movie_id=movie_id,
                user_id=user_id,
                description=description,
                rating=rating
            )
            db.session.add(review)
            db.session.commit()
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_all_reviews_data():
        """
            performs read operation on reviews table to return a dictionary of reviews record dictionary
        :return:
        """
        try:
            review_data_dict = {}
            reviews_details = db.session.query(Reviews).all()
            for review_detail in reviews_details:
                user_id = review_detail.user_id

                if user_id not in review_data_dict:
                    review_data_dict[user_id] = []

                review_data_dict[user_id].append({
                    'description': review_detail.description,
                    'rating': review_detail.rating,
                    'movie_id': review_detail.movie_id
                })
            return review_data_dict
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_all_ids():
        """
            performs a read operation on users table to return a list containing all users ids
        :return:
        """
        try:
            all_ids_list = []
            all_userids = db.session.query(Users.id, Users).all()
            for user in all_userids:
                all_ids_list.append(user.id)
            return all_ids_list
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def update_user_movie(user_id, movie_id, genre_id, director, year, review_description, review_rating):
        """
            performs an update operation on movies table to update some records fields
        :param user_id:
        :param movie_id:
        :param genre_id:
        :param director:
        :param year:
        :param review_description:
        :param review_rating:
        :return:
        """
        try:
            movie_to_update = db.session.query(User_movies).filter(User_movies.movie_id == movie_id,
                                                                   User_movies.user_id == user_id).one()
            if movie_to_update:
                movie_to_update.director = director
                movie_to_update.year = year
                movie_to_update.genre_id = genre_id
                db.session.commit()

            if review_description:
                review_to_update = db.session.query(Reviews).filter(Reviews.movie_id == movie_id,
                                                                    Reviews.user_id == user_id).one()
                if review_to_update:
                    review_to_update.description = review_description
                    review_to_update.rating = review_rating
                    db.session.commit()
                db.session.close()
                return "Movie details updated successfully"
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError,
                sqlalchemy.exc.IntegrityError):
            return None

    @staticmethod
    def delete_user_movie(user_id, movie_id):
        """
            performs a delete operation on user table to delete a record which satisfy the queried conditions
        :param user_id:
        :param movie_id:
        :return:
        """
        try:
            movie_to_delete = db.session.query(User_movies).filter(User_movies.movie_id == movie_id,
                                                                   User_movies.user_id == user_id).one()
            if movie_to_delete:
                db.session.delete(movie_to_delete)
                db.session.commit()
            db.session.close()
            return "Movie successfully deleted"
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def delete_movie(movie_id):
        """
            performs a delete operation on user table to delete a record which satisfy the queried conditions
        :param movie_id:
        :return:
        """
        try:
            movie_to_delete = db.session.query(Movies).filter(Movies.id == movie_id).one()

            if movie_to_delete:
                # Del all movies with the movie id in the user_movies database
                try:
                    user_movies_to_delete = db.session.query(User_movies).filter(User_movies.movie_id == movie_id).all()
                    for user_movie_to_del in user_movies_to_delete:
                        db.session.delete(user_movie_to_del)
                except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
                    pass
                # Del all user review with the movie id in the user_reviews database
                try:
                    movie_reviews_to_del = db.session.query(Reviews).filter(Reviews.movie_id == movie_id).all()
                    for movie_review_to_del in movie_reviews_to_del:
                        db.session.delete(movie_review_to_del)
                except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
                    pass

            title = movie_to_delete.title
            db.session.delete(movie_to_delete)
            db.session.commit()
            db.session.close()

            return f"The Movie: {title.title()} - successfully deleted"
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def delete_user_review(user_id, movie_id):
        """
            performs a delete operation on reviews table to delete a record which satisfy the queried conditions
        :param user_id:
        :param movie_id:
        :return:
        """
        try:
            review_to_delete = db.session.query(Reviews).filter(Reviews.movie_id == movie_id,
                                                                Reviews.user_id == user_id).one()
            if review_to_delete:
                db.session.delete(review_to_delete)
                db.session.commit()
            db.session.close()
            return "Review successfully deleted"
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_usermovie_director_year(user_id, movie_id):
        """
            performs a read operation on users table to some record fields which satisfied the queried conditions
        :param user_id:
        :param movie_id:
        :return:
        """
        try:
            movie_director_year = db.session.query(User_movies.director, User_movies.year, User_movies.title) \
                .filter(User_movies.user_id == user_id, User_movies.movie_id == movie_id).one()
            return movie_director_year.director, movie_director_year.year, movie_director_year.title
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_userreview_description(user_id, movie_id):
        """
            performs a read operation on reviews table to return some record fields which satisfy the queried conditions
        :param user_id:
        :param movie_id:
        :return:
        """
        try:
            review_description = db.session.query(Reviews.description) \
                .filter(Reviews.user_id == user_id, Reviews.movie_id == movie_id).one()
            return review_description.description
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_genre_details():
        """
            performs read operation on genre table which returns all genre data based on the queried conditions
        :return:
        """
        try:
            genres_details_list = []
            genres_details = db.session.query(Genres).all()
            for genre_detail in genres_details:
                genres_details_list.append({"id": genre_detail.id, "title": genre_detail.title,
                                            "description": genre_detail.description})
            return genres_details_list
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def delete_user(user_id):
        """
            performs a delete operation on user table to delete a record which satisfy the queried conditions
        :param user_id:
        :return:
        """
        try:
            user_to_delete = db.session.query(Users).filter(Users.id == user_id).one()
            if user_to_delete:
                db.session.delete(user_to_delete)

            movies_to_delete = db.session.query(User_movies).filter(User_movies.user_id == user_id).all()
            if movies_to_delete:
                for movie in movies_to_delete:
                    db.session.delete(movie)

            db.session.commit()
            db.session.close()

            return "User successfully deleted"
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_user(user_id):
        """
            performs a read operation on users table to return a list containing all users ids
        :return:
        """
        try:
            user = db.session.query(Users).filter(Users.id == user_id).one()
            return user
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None

    @staticmethod
    def get_user_object(email):
        """
            performs read operation on users table to return a dictionary of user_ids and usernames
            of all users
        :return:
        """
        try:
            user_object = db.session.query(Users).filter(Users.email == email).one()
            return user_object
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None


    @staticmethod
    def update_password(email, new_password):
        try:
            user = db.session.query(Users).filter(Users.email == email).one()
            user.set_password(new_password)
            db.session.commit()
            db.session.close()
            return True
        except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError):
            return None