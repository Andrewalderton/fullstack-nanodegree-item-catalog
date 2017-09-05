Item Catalog
============

## Description

An item catalog web app created using Flask for the Udacity Full Stack Nanodegree. The applicaiton provides a list of items within a variety of categories and integrates third party user registration and authentication. Authenticated users have the ability to post, edit, and delete their own items and categories.

## Setup

You will need Vagrant and Virtualbox installed in order to run the app.

Download or clone the repository.

Clone the [Udacity virtual machine repository](https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant), which contains the vagrant file needed to run the applicaiton.

Copy or move the data from the Item Catalog repository first downloaded into the catalog folder of the vagrant repository. Navigate to this folder before launching the app.

## Usage

Launch the Vagrant virtual machine by running `vagrant up` in the command line. Then log in using `vagrant ssh`. Follow any prompts to change into the Vagrant shared directory.

Install the dependency libraries (Flask, sqlalchemy, requests and oauth2client) by running `pip install -r requirements.txt`

Add sample database categories and items using `python books_database.py`

To run the app, enter `python application.py`, then navigate to `localhost:8000` in the browser.

## JSON Endpoints

`/categories/JSON` - Returns data for all categories.

`/categories/<int:category_id>/JSON` - Returns data for all items of a specific category.

`/catalog/<int:category_id>/books/<int:book_id>/JSON` - Returns data regarding a specific category item.