#!/usr/bin/env python
import string, random, json, httplib2, requests
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_config import User, Category, Book, Base
from flask import Flask, g, render_template, flash, redirect, url_for, request, jsonify, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError


app = Flask(__name__)

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

Session = sessionmaker(bind=engine)
session = Session()

# Check if user already exists
def checkUser(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
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


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
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

    flash("Login Successful")

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html',
                           categories=categories,
                           user_id=login_session['user_id'])


# Create a new category
@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        if not request.form['name']:
            name = request.form['name']
            description = request.form['description']
            error = 'Please enter a category name'
            return render_template('new-category.html',
                                   error=error,
                                   name=name,
                                   description=description)

        new_category = Category(name=request.form['name'],
                                description=request.form['description'],
                                user_id=login_session['user_id'])
        session.add(new_category)
        flash('New category %s Successfully Created' % new_category.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('new-category.html')


# Edit a category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    edited_category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        if login_session['user_id'] != edited_category.user_id:
            error = 'Sorry, you do not have permission to edit this category.'
            return render_template('edit-category.html',
                                   name=edited_category.name,
                                   description=edited_category.description,
                                   error=error)
        elif request.form['name']:
            edited_category.name = request.form['name']
            edited_category.description = request.form['description']
            session.add(edited_category)
            session.commit()
            flash('category Successfully Edited %s' % edited_category.name)
            return redirect(url_for('showCategories'))
        else:
            error = 'Category name is required.'
            return render_template('edit-category.html',
                                   name=edited_category.name,
                                   description=edited_category.description,
                                   error=error)
    else:
        return render_template('edit-category.html',
                               name=edited_category.name, description=edited_category.description)


# Delete a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category_to_delete = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if login_session['user_id'] != category_to_delete.user_id:
            error = 'Sorry, you do not have permission to delete this category.'
            return render_template('delete-category.html',
                                   category_id=category_id,
                                   error=error)
        else:
            session.delete(category_to_delete)
            flash('%s Successfully Deleted' % category_to_delete.name)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        return render_template('delete-category.html',
                               category=category_id)


# Show a category's books
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/books/')
def showBook(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    books = session.query(Book).filter_by(category_id=category_id).all()
    return render_template('books.html',
                           books=books,
                           category=category,
                           user_id=login_session['user_id'])


# Show a single book
@app.route('/categories/<int:category_id>/<int:book_id>/')
@app.route('/categories/<int:category_id>/books/<int:book_id>/')
def singleBook(category_id, book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return render_template('book-item.html',
                           user_id=login_session['user_id'],
                           book=book)


# Create a new book item
@app.route('/categories/<int:category_id>/books/new/', methods=['GET', 'POST'])
def newBook(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']

        if not request.form['title']:
            error_title = 'Please enter a title'
            return render_template('new-book.html',
                                   category_id=category_id,
                                   error_title=error_title,
                                   title=title,
                                   author=author,
                                   description=description)

        if not request.form['author']:
            error_author = 'Please enter an author'
            return render_template('new-book.html',
                                   category_id=category_id,
                                   error_author=error_author,
                                   title=title,
                                   author=author,
                                   description=description)

        new_book = Book(title=str(title),
                        author=str(author),
                        description=str(description),
                        category_id=category_id,
                        user_id=login_session['user_id'],
                        img='')
        session.add(new_book)
        session.commit()
        flash('New Book, %s, Successfully Created' % (new_book.title))
        return redirect(url_for('showBook', category_id=category_id))
    else:
        return render_template('new-book.html', category_id=category_id)


# Edit a book item
@app.route('/categories/<int:category_id>/books/<int:book_id>/edit/', methods=['GET', 'POST'])
def editBook(category_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')

    edited_book = session.query(Book).filter_by(id=book_id).one()
    category = session.query(Category).filter_by(id=category_id).one()

    if login_session['user_id'] != edited_book.user_id:
        error = 'Sorry, you can\'t edit other users\' posts.'
        return render_template('book-item.html',
                               error=error,
                               title=edited_book.title,
                               author=edited_book.author,
                               description=edited_book.description,
                               category_id=category_id,
                               book_id=book_id)

    if request.method == 'POST':
        if not request.form['title']:
            error_title = 'Please enter a title'
            return render_template('edit-book.html',
                                   title=edited_book.title,
                                   author=edited_book.author,
                                   description=edited_book.description,
                                   category_id=category.id,
                                   error_title=error_title)
        else:
            edited_book.title = request.form['title']

        if not request.form['author']:
            error_author = 'Please enter an author'
            return render_template('edit-book.html',
                                   title=edited_book.title,
                                   author=edited_book.author,
                                   description=edited_book.description,
                                   category_id=category.id,
                                   error_author=error_author)
        else:
            edited_book.author = request.form['author']

        if request.form['description']:
            edited_book.description = request.form['description']

        session.add(edited_book)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('showBook', category_id=category_id))
    else:
        return render_template('edit-book.html',
                               title=edited_book.title,
                               author=edited_book.author,
                               description=edited_book.description,
                               category_id=category.id)


# Delete a book item
@app.route('/categories/<int:category_id>/books/<int:book_id>/delete/', methods=['GET', 'POST'])
def deleteBook(category_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(id=category_id).one()
    book_to_delete = session.query(Book).filter_by(id=book_id).one()

    if request.method == 'POST':
        session.delete(book_to_delete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('showBook', category_id=category_id))
    else:
        return render_template('delete-book.html',
                               category_id=category.id,
                               book_id=book_to_delete.id)


# JSON APIs to view category Information
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[r.serialize for r in categories])


@app.route('/categories/<int:category_id>/JSON')
def categoryJSON(category_id):
    items = session.query(Book).filter_by(
        category_id=category_id).all()
    return jsonify(Books=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/books/<int:book_id>/JSON')
def bookJSON(category_id, book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)


if __name__ == '__main__':
    app.secret_key = 'secret_muffin'
    app.run(debug=DEBUG, host=HOST, port=PORT)
