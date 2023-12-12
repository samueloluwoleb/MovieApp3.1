# The Movieweb_app project


## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Application Structure](#application-structure)
* [Core Functionalities](#core-functionalities)

## General info
MoviWeb App project is a full-featured, dynamic web application that allows user to query for any movie,
the movie info is obtained through API from OMDB website and the movie gets added to their personal list of favourite movies

## Technologies
Project is created with:
* Python
* Html 5
* CSS
* Flask
* API
* SQLITE database
	
## Application Structure
The MoviWeb application will consist of several key parts:
* User Interface (UI): An intuitive web interface built using Flask, HTML, and CSS. It will provide forms for adding, updating, and deleting movies, as well as a method to select a user.
* Data Management: A Python class to handle operations related to the sqlite database
* data source. This class should expose functions for listing all users, listing a user’s movies, and updating a user’s movie.
* Persistent Storage: An sqlite database file to store user and movie data. This file will act as the database for your application.

## Core Functionalities

The core functionalities of your MoviWeb application will include:
* User Selection: The ability for a user to select their identity from a list of users.
* Movie Management: After a user is selected, the application will display a list of their favorite movies. From here, users should be able to Add a movie: Include the movie’s name, director, year of release, and rating.
* Delete a movie: Remove a movie from their list.
* Update a movie: Modify the information of a movie from their list.
* List all movies: View all the movies on their list.
* Data Source Management: Use your Python class to manage interactions with the sqlite database data source.