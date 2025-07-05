from flask import Flask, render_template, request, flash, redirect, url_for, get_flashed_messages, g, make_response, \
    session, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from jinja2 import TemplateNotFound
from datamanager.sql_data_manager import *
from config import config
from flask_babel import Babel, refresh
from datamanager.movie_recommendation import get_movie_recommendation_from_openai
from flask_mail import Mail, Message
import secrets

# Initialize flask app and set some parameters value
app = Flask(__name__)

# Initialize the LoginManager object with the application object
login_manager = LoginManager(app)


def get_locale():
    user_language = getattr(g, 'user_language', None)

    if user_language:
        return user_language

    return request.accept_languages.best_match(
        app.config['LANGUAGES'].keys()
    )


# Initialize Flask-BabelEx object with the flask application object and the locale_selector
babel = Babel(app, locale_selector=get_locale)

# initialize the app with the extension and configuration file
app.config.from_object(config)
mail = Mail(app)

db.init_app(app)
reset_tokens = {}


# create an object of the JSONDataManager class
def object_create():
    try:
        return SQLiteDataManager()
    except FileNotFoundError:
        return render_template('404.html')


# assigns the object to a variable
data_manager = object_create()

# creates all database tables and also records for Genres table
with app.app_context():
    db.create_all()
    data_manager.create_genre_record()


def user_logout():
    session.pop('darkmode', None)
    logout_user()


# Configure the login manager
@login_manager.user_loader
def load_user(user_id):
    user = data_manager.get_user(user_id)
    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    """
        Gets triggered when client sends a get request to this route.
        It renders the index.html webpage
    :return:
    """
    # get the admin email from the configuration file
    admin_email = app.config['ADMIN_EMAIL']
    try:
        # Handles the flash message sent from other sessions
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        # gets the form data from POST url
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            # Logic for admin
            if email == admin_email:
                pass_verified = ""
                user_info = data_manager.get_userid_password(email)
                pass_verified = data_manager.verify_user_password(email, password)

                if user_info and pass_verified:
                    user_object = data_manager.get_user_object(email)
                    login_user(user_object)
                    flash("Logged in successful", "success")

                    return redirect(url_for('admin'))
                else:
                    flash(f"Login Failed: Please verify you entered the correct email and password", "success")
                    return redirect(url_for('index'))

            else:  # Logic for all other users
                pass_verified = ""
                user_info = data_manager.get_userid_password(email)
                pass_verified = data_manager.verify_user_password(email, password)

                if user_info and pass_verified:
                    user_object = data_manager.get_user_object(email)
                    login_user(user_object)
                    flash("Logged in successful", "success")

                    user_id = user_info.get("userid")
                    return redirect(url_for("user_profile", user_id=user_id))
                else:
                    flash(f"Login Failed: Please verify you entered the correct email and password", "success")
                    return redirect(url_for('index'))

        else:
            return render_template('index.html', flash_message=flash_message)
    except TemplateNotFound:
        return "Template not found", 404


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    """
        Gets triggered when the client sends either a get request to this route.
        Parses response data and renders the appropriate html document based on app state and condition statements
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        # Handles the flash message sent from other sessions
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        # gets the form data from POST url
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["password1"]
            gender = request.form["gender"]

            if password != confirm_password:
                flash(f"The password doesn't match, try again", "success")
                return redirect(url_for("add_user"))

            # calls the add_user method which performs the add operation on the users table
            data_manager.add_user(username, email, password, gender)

            # sends data of this session to the redirected url
            flash(f"The user: {username} - has been added successfully.", "success")
            return redirect(url_for("admin"))
        else:
            return render_template('add_user.html', flash_message=flash_message)
    except(AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, TemplateNotFound,
           sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """
        Gets triggered when the client sends either a get request to this route.
        Parses response data and renders the appropriate html document based on app state and condition statements
    :return:
    """
    try:
        # Handles the flash message sent from other sessions
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        # gets the form data from POST url
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["password1"]
            gender = request.form["gender"]

            if password != confirm_password:
                flash(f"The password doesn't match, try again", "success")
                return redirect(url_for("sign_up"))

            # calls the add_user method which performs the add operation on the users table
            data_manager.add_user(username, email, password, gender)

            # sends data of this session to the redirected url
            flash(f"Welcome {username.title()} !!! - Hover on Menu to login.", "success")
            return redirect(url_for("index"))
        else:
            return render_template('sign_up.html', flash_message=flash_message)
    except(AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, TemplateNotFound,
           sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/logout')
def logout():
    user_logout()
    g.user_language = 'en'
    refresh()
    flash('You have successfully logged out, hover on menu to log back in', "success")
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
@login_required
def add_user_movie(user_id):
    """
        Gets triggered when the client sends either a get request to this route.
        Parses response data and renders the appropriate html document based on app state and other condition statements
    :param user_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        # gets the form data from POST url

        mode = session['darkmode']

        if request.method == "POST":
            title = request.form["title"].strip()
            rating = request.form["rating"]
            director = request.form["director"]
            year = request.form["year"]
            genre_id = int(request.form["genre_id"])

            # calls the add_movie method which performs the add operation on the movies and user_movies tables
            message = data_manager.add_movie(title, rating, director, year, genre_id, user_id)

            # sends data of this session to the redirected url
            flash(f"{message}", "success")
            return redirect(url_for("user_profile", user_id=user_id, ))
        else:
            user_id = user_id
            all_ids = data_manager.get_all_ids()
            if user_id in all_ids:
                # checks the state of GET request to determine the template to render and the data to send
                searched_movie = request.args.get("searched_movie")
                if searched_movie is None:
                    state = 'get'
                    return render_template('add_user_movie.html', state=state, user_id=user_id, mode=mode)
                else:
                    title, rating, director, year = data_manager.get_movie_info_api(searched_movie)

                    if title is None:
                        flash(f"There are no movies matching your searched movie -- {searched_movie}", "success")
                        return redirect(url_for("user_profile", user_id=user_id))
                    else:
                        return render_template('add_user_movie.html', title=title, year=year, rating=rating,
                                               director=director, user_id=user_id, mode=mode)
    except(AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, TemplateNotFound,
           sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/toggle_darkmode', methods=['POST'])
def toggle_darkmode():
    if request.method == 'POST':
        # Toggle the dark_mode session variable
        data = request.get_json()
        if data.get('dark_mode') == "true":
            session['darkmode'] = "true"
        if data.get('dark_mode') == "false":
            session['darkmode'] = "false"
        return jsonify(success=True, dark_mode=session['darkmode'])


@app.route('/users/<int:user_id>')
@login_required
def user_profile(user_id):
    """
        Gets triggered when the client sends a get request to the route.
        It takes a user_id parameter obtained from the request and renders the user.html webpage which
        display the movies of a particular user
    :param user_id:
    :return:
    """
    try:
        # Checks if user trying to access the endpoint is currently logged in and also whether user is admin or not
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))

        # Set state for darkmode to be false whenever user logs in
        if not session.get('darkmode'):
            session['darkmode'] = "false"
            mode = session['darkmode']
        else:
            mode = session['darkmode']

        # Handles the flash message sent from other sessions
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        # gets all the records in reviews table
        reviews_data = data_manager.get_all_reviews_data()
        user_movies_list = data_manager.get_user_movies(user_id)
        name = data_manager.get_user_name(user_id)
        genres_details = data_manager.get_genre_details()
        return render_template('user_profile.html', user_movies=user_movies_list, user_id=user_id, name=name,
                               flash_message=flash_message, reviews_data=reviews_data, genres_details=genres_details, mode=mode)
        # response=response)
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/users/<int:user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
@login_required
def update_user_movie(user_id, movie_id):
    """
        Gets triggered when the client sends either a get or post request to this route.
        Parses response data and renders the appropriate html document based on app state and other condition statements
    :param user_id:
    :param movie_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))

        # Set state for dark-mode whenever user logs in
        mode = session['darkmode']

        if request.method == "POST":
            title = request.form["title"].strip()
            director = request.form["director"]
            year = request.form["year"]
            rating = float(request.form["rating"])
            genre_id = int(request.form["genre_id"])

            # catches error raised when a movie with no review is updated, this set the description value to None \
            # and it is used to determine the state of review description field to be visible or not
            try:
                description = request.form["description"]
            except KeyError:
                description = None

            message = data_manager.update_user_movie(user_id, movie_id, genre_id, director, year, description, rating)

            flash(message, "success")
            return redirect(url_for("user_profile", user_id=user_id, title=title, mode=mode))
        else:
            movie_director, movie_year, movie_title = data_manager.get_usermovie_director_year(user_id, movie_id)
            review_description = data_manager.get_userreview_description(user_id, movie_id)
            return render_template('update_user_movie.html', director=movie_director, year=movie_year,
                                   description=review_description, title=movie_title,
                                   user_id=user_id, movie_id=movie_id, mode=mode)
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
@login_required
def delete_user_movie(user_id, movie_id):
    """
        Gets triggered when the client sends a get request to the route
        Parses response data and performs the appropriate operations based on app state and other condition statements
    :param user_id:
    :param movie_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        message = data_manager.delete_user_movie(user_id, movie_id)

        flash(message, "success")
        return redirect(url_for("user_profile", user_id=user_id))
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/admin/del_movie')
@login_required
def delete_movie():
    """
    :param movie_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        movie_id = request.args["movie_id"]
        message = data_manager.delete_movie(movie_id)
        if message:
            flash(f"{message}", "success")
            return redirect(url_for("admin"))
        else:
            flash(f"The ID you entered doesn't exist", "success")
            return redirect(url_for("admin"))
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/users/<int:user_id>/delete_review/<int:movie_id>')
@login_required
def delete_user_review(user_id, movie_id):
    """
        Gets triggered when the client sends a get request to the route
        Parses response data and performs the appropriate operations based on app state and other condition statements
    :param user_id:
    :param movie_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        message = data_manager.delete_user_review(user_id, movie_id)

        flash(message, "success")
        return redirect(url_for("user_profile", user_id=user_id))
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/users')
@login_required
def users():
    """
        Gets triggered when the client sends a get request to the route
        It renders users.html webpage which displays users' names
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        users = data_manager.get_all_users()
        return render_template('users.html', users=users, flash_message=flash_message)
    except (AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, sqlalchemy.exc.NoResultFound,
            sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/reviews/<int:user_id>/review_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def add_user_review(movie_id, user_id):
    """
        Gets triggered when the client sends a get request to the route
        Parses response data and performs the appropriate operations based on app state and other condition statements
    :param movie_id:
    :param user_id:
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == user_id or current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        if request.method == "POST":
            description = request.form["description"]
            rating = float(request.form["rating"])

            data_manager.add_user_review(movie_id, user_id, description, rating)

            flash(f"Review successfully added to the movie", "success")
            return redirect(url_for("user_profile", user_id=user_id))
    except(AttributeError, ValueError, TypeError, FileNotFoundError, KeyError, TemplateNotFound,
           sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError):
        return render_template('404.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """
        Gets triggered when client sends a get request to this route.
        It renders the index.html webpage
    :return:
    """
    try:
        if not (current_user.is_authenticated() and (current_user.id == 1)):
            logout()
            flash("{{_('You are not authorize to view the page, please log in')}}", "success")
            return redirect(url_for("index"))
        # Handles the flash message sent from other sessions
        flash_message = None
        if len(get_flashed_messages()) > 0:
            flash_message = get_flashed_messages()[0]

        if request.method == "POST":
            if "del_user_id" in request.form:
                del_user_id = request.form["del_user_id"]
                del_success = data_manager.delete_user(del_user_id)
                if del_success:
                    flash(f"{del_success}", "success")
                    return redirect(url_for("admin"))
                else:
                    flash(f"Please check the user ID", "success")
                    return redirect(url_for("admin"))

            if "user_profile_id" in request.form:
                user_id = request.form["user_profile_id"]
                return redirect(url_for("user_profile", user_id=user_id))

        else:
            return render_template('admin.html', flash_message=flash_message)
    except TemplateNotFound:
        return "Template not found", 404


@app.route('/admin/add_movie', methods=['GET', 'POST'])
@login_required
def admin_add_movie():
    try:
        if not (current_user.is_authenticated() and (current_user.id == 1)):
            logout()
            flash("You are not authorize to view the page, please log in", "success")
            return redirect(url_for("index"))
        if request.method == "GET":
            searched_movie = request.args['movie_name']
            title, rating, director, year = data_manager.get_movie_info_api(searched_movie.strip())
            if title is None:
                flash(f"There are no movies matching your searched movie -- {searched_movie}", "success")
                return redirect(url_for("admin"))
            else:
                return render_template("add_movie.html", title=title, rating=rating, director=director, year=year)
        else:
            title = request.form["title"].strip()
            rating = request.form["rating"]
            director = request.form["director"]
            year = request.form["year"]

            movie_title = data_manager.get_all_movies_title(title)
            if movie_title:
                message = f"The movie -- {title} -- already exists in your catalogue"
                flash(f"{message}", "success")
                return redirect(url_for("admin"))
            else:
                # calls the add_movie method which performs the add operation on the movies and user_movies tables
                data_manager.add_movies_record(title, rating, director, year)
                # sends data of this session to the redirected url
                flash(f"The movie: {title.title()} successfully added", "success")
                return redirect(url_for("admin"))
    except TemplateNotFound:
        return "Template not found", 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    # Set the language based on user preferences (from cookies, for example)
    user_language = request.cookies.get('language', None)

    if user_language in app.config['LANGUAGES']:
        g.user_language = user_language
        refresh()  # Refresh translations for the selected language
    else:
        # If no language is set, use the default language
        g.user_language = 'en'
        refresh()


@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        language = request.form['language']
        print(language)
        response = make_response(redirect(request.referrer))
        response.set_cookie('language', language)
        return response


@app.route('/enter_email')
def enter_email():
    return render_template('enter_email.html')


def email_exists_in_your_database(email):
    # Checks if email exists and returns True if the email exists, False otherwise
    user = data_manager.get_user_object(email)
    if user:
        return True
    else:
        return False


def send_reset_email(email, token):
    # Craft the reset email
    subject = 'Password Reset Request'
    print(subject)
    reset_link = url_for('reset_password', token=token, _external=True)
    print('reset_link', reset_link)
    body = f'Click the following link to reset your password: {reset_link}'

    # Send the email
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)


@app.route('/password_reset_email', methods=['GET', 'POST'])
def password_reset_email():
    if request.method == 'POST':
        email = request.form.get('email')
        print('email', email)

        # Check if the email exists in your database (you need to implement this)
        # If the email exists, generate a reset token and send the reset email
        if email_exists_in_your_database(email):
            token = secrets.token_urlsafe(16)
            reset_tokens[email] = token
            print("token", token)

            # Send the reset email
            send_reset_email(email, token)
            print('email successfully sent')

            flash('Password reset email sent. Check your email for instructions.', 'success')
            return redirect(url_for('index'))

        else:
            flash('Email not found. Please check your email address.', 'error')

    return render_template('password_reset_email.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = get_email_for_token(token)
    print(email)

    if not email:
        flash('Invalid or expired token. Please request a new password reset.', 'error')
        return redirect(url_for('password_reset_email'))

    if request.method == 'POST':
        # gets the form data from POST url
        new_password = request.form["password"]
        confirm_password = request.form["password1"]

        if new_password != confirm_password:
            flash(f"The password doesn't match, request a new password reset link", "success")
            return redirect(url_for("index"))

        update_password_in_your_database(email, new_password)
        flash("Password updated, please re-login with the new password", 'success')
        return redirect(url_for('index'))

    return render_template('new_password.html', email=email, token=token)


@app.route('/ai_api/<int:user_id>')
def ai_api(user_id):
    # Queries chatgpt and get the response for movies recommendation
    all_movies_titles = data_manager.get_user_movies_titles(user_id)

    movies_prompt_for_ai = f"Based on the story plot of these movies: {all_movies_titles}, " \
                           f"recommend 5 movies for me"

    # for openai api 
    # response = get_movie_recommendation_from_openai(movies_prompt_for_ai)

    response = get_movie_recommendation_from_openai(movies_prompt_for_ai)
    return response


def get_email_for_token(token):
    for email, t in reset_tokens.items():
        if t == token:
            return email
    return None


def update_password_in_your_database(email, new_password):
    message = data_manager.update_password(email, new_password)
    return message


if __name__ == '__main__':
    # Launch the Flask dev server
    app.run(host="0.0.0.0", port=5004)
