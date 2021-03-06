#!/usr/bin/env python2

import string
import random
import json
from functools import wraps
import httplib2
import requests
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_config import User, Category, Book, Base
from flask import (
    Flask, g, render_template, flash, redirect, url_for, request, jsonify,
    make_response
)
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError


# App setup
app = Flask(__name__)

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

CLIENT_ID = (json.loads(open('client_secrets.json', 'r').read())['web']
             ['client_id'])
APPLICATION_NAME = "Item Catalog"

# Connect to Database and create database session
engine = create_engine('postgres://cppuchkbswutrx:2ca2a869db9b201d744f563bb5ddf63eb5159ad9c1ef9cc11e3d2aa070fa6663@ec2-23-21-88-45.compute-1.amazonaws.com:5432/dekf8akjo5gdgk')
Base.metadata.bind = engine

Session = sessionmaker(bind=engine)
session = Session()


# Check if user already exists
def checkUser(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Save new user's details to the database after logging in
def createUser(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Check if item already exists in the database
def checkBook(title):
    try:
        title_search = session.query(Book).filter_by(title=title).one()
        return title_search.title
    except Exception:
        return None


# Check if category already exists in the database
def checkCategory(name):
    try:
        category_search = session.query(Category).filter_by(name=name).one()
        return category_search.name
    except Exception:
        return None


# Check user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('Sorry, you do not have permission to access this page.')
            return redirect('/login')
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Log out the current User
@app.route('/logout')
def logout():
    if login_session['provider'] == 'google':
        gdisconnect()
        del login_session['access_token']
        del login_session['gplus_id']

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']

    return redirect(url_for('showCategories'))


# Google Plus login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists
    user_id = checkUser(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("You are now logged in as %s" % login_session['username'])
    return redirect(url_for('showCategories'))


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for given '
                                            'user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    """List the categories and their descriptions on the main page"""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if categories:
        return render_template('categories.html',
                               categories=categories)
    else:
        error = 'Sorry, there is nothing to display here yet.'
        return render_template('categories.html',
                               error=error)


# Create a new category
@app.route('/categories/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    """Create a new category"""
    if request.method == 'POST':
        if not request.form['name']:
            name = request.form['name']
            description = request.form['description']
            error = 'Please enter a category name'
            return render_template('new-category.html',
                                   error=error,
                                   name=name,
                                   description=description)

        if checkCategory(request.form['name']) is None:
            new_category = Category(name=request.form['name'],
                                    description=request.form['description'],
                                    user_id=login_session['user_id'])
            session.add(new_category)
            flash('New category %s Successfully Created' % new_category.name)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            error = 'This category already exists'
            return render_template('new-category.html',
                                   description=request.form['description'],
                                   error=error)
    else:
        return render_template('new-category.html')


# Edit a category
@app.route('/categories/<path:category_name>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    """Edit a category's name and description"""
    edited_category = (
        session.query(Category).filter_by(name=category_name).one()
    )

    if request.method == 'POST':
        if login_session['user_id'] != edited_category.user_id:
            error = 'Sorry, you do not have permission to edit this category.'
            return render_template('edit-category.html',
                                   error=error,
                                   category=edited_category)
        elif not request.form['name']:
            error = 'Please enter a category name'
            return render_template('edit-category.html',
                                   error=error,
                                   category=edited_category)

        elif checkCategory(request.form['name']) is None or (
                request.form['name'] == edited_category.name):
            edited_category.name = request.form['name']
            edited_category.description = request.form['description']
            session.add(edited_category)
            session.commit()
            flash('%s Category Successfully Edited' % edited_category.name)
            return redirect(url_for('showCategories'))
        else:
            error = 'This category already exists'
            return render_template('edit-category.html',
                                   error=error,
                                   category=edited_category)
    else:
        return render_template('edit-category.html',
                               category=edited_category)


# Delete a category
@app.route('/categories/<path:category_name>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    """Delete a category if created by the current user"""
    category_to_delete = session.query(
        Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        if login_session['user_id'] != category_to_delete.user_id:
            error = 'Sorry, you can only delete categories that you created.'
            return render_template('delete-category.html',
                                   error=error,
                                   category=category_to_delete)
        else:
            session.delete(category_to_delete)
            flash('%s Successfully Deleted' % category_to_delete.name)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        return render_template('delete-category.html',
                               category=category_to_delete)


# Show a category's books
@app.route('/categories/<path:category_name>/')
def showBook(category_name):
    """Display book title, author, description and image for each book in a
     category."""
    category = session.query(Category).filter_by(name=category_name).one()
    books = session.query(Book).filter_by(category=category.id).all()
    return render_template('books.html',
                           books=books,
                           category=category)


# Show a single book
@app.route('/categories/<path:category_name>/<path:book_title>/')
def singleBook(category_name, book_title):
    """Display the information relating to a single item"""
    category = session.query(Category).filter_by(name=category_name).one()
    book = session.query(Book).filter_by(title=book_title).one()
    return render_template('book-item.html',
                           book=book,
                           category=category)


# Create a new book item
@app.route('/categories/<path:category_name>/new/', methods=['GET', 'POST'])
@login_required
def newBook(category_name):
    """Create a new entry in a specific category"""
    category = session.query(Category).filter_by(name=category_name).one()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        image = request.form['img']

        if not request.form['title']:
            error_title = 'Please enter a title'
            return render_template('new-book.html',
                                   error_title=error_title,
                                   title=title,
                                   author=author,
                                   description=description,
                                   img=image)

        if not request.form['author']:
            error_author = 'Please enter an author'
            return render_template('new-book.html',
                                   error_author=error_author,
                                   title=title,
                                   author=author,
                                   description=description,
                                   img=image)

        if checkBook(title) is None:
            new_book = Book(title=str(title),
                            author=str(author),
                            description=str(description),
                            user_id=login_session['user_id'],
                            img=str(image),
                            category=category.id)
            session.add(new_book)
            session.commit()
            flash('New Book, %s, Successfully Created' % (new_book.title))
            return redirect(url_for('showBook', category_name=category.name))
        else:
            error = 'Sorry, this book already exists.'
            return render_template('new-book.html',
                                   error_title=error)
    else:
        return render_template('new-book.html')


# Edit a book item
@app.route('/categories/<path:category_name>/<path:book_title>/edit/',
           methods=['GET', 'POST'])
@login_required
def editBook(category_name, book_title):
    """Edit an item entry created by the current user"""
    edited_book = session.query(Book).filter_by(title=book_title).one()
    category = session.query(Category).filter_by(name=category_name).one()

    if login_session['user_id'] != edited_book.user_id:
        error = 'Sorry, you can\'t edit other users\' posts.'
        return render_template('book-item.html',
                               error=error,
                               book=edited_book,
                               category=category)

    if request.method == 'POST':
        if not request.form['title']:
            error_title = 'Please enter a title'
            return render_template('edit-book.html',
                                   error_title=error_title,
                                   book=edited_book,
                                   category=category)

        elif checkBook(request.form['title']) is None or (
                checkBook(request.form['title']) == edited_book.title
        ):
            edited_book.title = request.form['title']
        else:
            error = 'Sorry, this book title already exists'
            return render_template('edit-book.html',
                                   error_title=error,
                                   book=edited_book,
                                   category=category)

        if not request.form['author']:
            error_author = 'Please enter an author'
            return render_template('edit-book.html',
                                   error_author=error_author,
                                   book=edited_book,
                                   category=category)
        else:
            edited_book.author = request.form['author']

        if request.form['description']:
            edited_book.description = request.form['description']

        if request.form['img']:
            edited_book.img = request.form['img']

        session.add(edited_book)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('showBook', category_name=category.name))
    else:
        return render_template('edit-book.html',
                               book=edited_book,
                               category=category)


# Delete a book item
@app.route('/categories/<path:category_name>/<path:book_title>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteBook(category_name, book_title):
    """Delete an entry previously created by the user"""
    category = session.query(Category).filter_by(name=category_name).one()
    book_to_delete = session.query(Book).filter_by(title=book_title).one()

    if request.method == 'POST':
        session.delete(book_to_delete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('showBook', category_name=category_name))
    else:
        return render_template('delete-book.html',
                               category_name=category_name,
                               book_id=book_to_delete.id)


# JSON APIs to view category Information
@app.route('/categories/JSON')
def categoriesJSON():
    """Return JSON data relating to the whole catalog"""
    categories = session.query(Category).all()
    return jsonify(Categories=[r.serialize for r in categories])


@app.route('/categories/<path:category_name>/JSON')
def categoryJSON(category_name):
    """Return JSON data for a specific category"""
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Book).filter_by(
        category=category.id).all()
    return jsonify(Books=[i.serialize for i in items])


@app.route('/categories/<path:category_name>/<path:book_title>/JSON')
def bookJSON(category_name, book_title):
    """Return JSON data for a single item entry"""
    book = session.query(Book).filter_by(title=book_title).one()
    return jsonify(Book=book.serialize)


# if __name__ == '__main__':
app.secret_key = 'secret_muffin'
    # app.run(debug=DEBUG, host=HOST, port=PORT)
