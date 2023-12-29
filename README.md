# The Movieweb_app project

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Application Structure](#application-structure)
* [Core Functionalities](#core-functionalities)

## General info
MoviWeb App project is a full-featured, dynamic web application that allows users to create their personal account, query for any movie title, the movie info is obtained through API call to OMDB website and the movie gets added to their personal list of favourite movies. User can add movies to their movie catalogue, update movie info, and delete a movie as well.

## Technologies
Project is created with:
* Python
* Html 5
* CSS
* Flask
* API
* SQLITE database
* OpenAI API 
	
## Application Structure

The MoviWeb application will consist of several key parts:

* User Interface (UI): An intuitive web interface built using Flask, HTML, and CSS. It will provide forms for adding, updating, and deleting movies, as well as a method to select a user.
* Data Management: A Python class to handle operations related to the sqlite database
* Data source. A python class should expose functions for operations such as: listing all users, listing a user’s movies, deleting a user movie, and updating a user’s movie.
* Persistent Storage: An sqlite database file to store user and movie data. This file will act as the database for your application.
* API calls: Api calls to different data source(OMDB website to get movie details and OpenAI website to get movie reccomendation)
  
## Core Functionalities

The core functionalities of your MoviWeb application will include:

* User Account Creation: The functionality  a uthat enables a user to create an account on the website using their email address and then log in into their account.
* Language Preference: The functionality that enables a user to choose the language they want the website to be displayed in. Languages are (English, Spanish and French)
* Authentication and Authorization: The functionality that enables user to be properly authenticated (using email and password) before granting application access and properly authorize to perform only specific operations that are allowed by their user status.
* Password Reset: User can reset their forgotten password and create a new one using their email address
* UI Display Preference: The functionality that enables the user to choose between Dark and Light mode
* Movie Reccomendation: The functionality that display a list of movies user would enjoy based on the movie from their catalogue
* Add a Movie: User can add movie to their catalogue
* Delete a Movie: User can delete movies from their list.
* Update a Movie: User can update movie details.
* Addd a Review: User can add a review to movies in their catalogue and also delete the review if they choose

## Project dependencies installation

You should install the projects dependencies package using the command:
pip install -r requirements. txt



