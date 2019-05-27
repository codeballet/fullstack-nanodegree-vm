from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort, g
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from models import Category, User, Item, Base

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
from flask_httpauth import HTTPBasicAuth
import requests, json


auth = HTTPBasicAuth()

app = Flask(__name__)
engine = create_engine('sqlite:///antiques.db')
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()


with open('client_secrets.json', 'r') as f:
    CLIENT_ID = json.loads(f.read())['web']['client_id']


####################################
# Authorisation and Authentication #
####################################

# Verify token or username / password for protected routes
@auth.verify_password
def verify_password(username_or_token, password):
    # Check for token
    try:
        user_id = User.verify_auth_token(username_or_token)
        if user_id:
            user = session.query(User).filter_by(user_id = user_id).one()
        else:
            user = session.query(User).filter_by(user_name = username_or_token).first()
            if not user or not user.verify_password(password):
                return False
        g.user = user
        return True
    except:
        return False


# Collect oauth user info and generate app token
@app.route('/oauth/<provider>', methods = ['POST'])
def login(provider):
    auth_code = request.json.get('auth_code')
    # Exchange one-time client code for oauth access token
    if provider == 'google':
        try:
            print 'starting oauth flow'
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
            print 'finished oauth flow'
        except FlowExchangeError:
            print 'inside FlowExchangeError'
            response = make_response(json.dumps('Failed to upgrade authorization code'), 401)
            response.headers['Content-type'] = 'application/json'
            return response

        # Check that oauth access_token is valid
        access_token = credentials.access_token
        print 'access token received: %s' % access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # Get user info from oauth provider
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        data = answer.json()
        user_name = data['name']
        user_picture = data['picture']
        user_email = data['email']

        # If user does not exist, create a new one
        user = session.query(User).filter_by(user_email = user_email).first()
        if not user:
            user = User(user_name = user_name, user_picture = user_picture, user_email = user_email)
            session.add(user)
            session.commit()

        # Generate token and send back to client
        token = user.generate_auth_token(600)
        return jsonify({"token": token.decode('ascii')})

    else:
        return 'Unrecognized Provider'



##################
# HTML endpoints #
##################

# Login page
@app.route('/login')
@app.route('/catalog/login')
def start():
    return render_template('login.html')


@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).order_by(Category.category_name).all()
    items = session.query(Item).order_by(desc(Item.item_date)).limit(10)
    list_categories = []
    for item in items:
        get_category = session.query(Category).filter_by(category_id = item.category_id).one()
        list_categories.append(get_category.category_name)
    return render_template('catalog.html', categories = categories, items = items, list_categories = list_categories)


@app.route('/catalog/newcategory', methods = ['GET', 'POST'])
def addCategory():
    if request.method == 'POST':
        if request.form['category_name']:
            newCategory = Category(category_name = request.form['category_name'])
            session.add(newCategory)
            session.commit()
            flash('New Category created!')
            return redirect(url_for('showCategory', category_name = newCategory.category_name))
        else:
            flash('You did not create a new Category')
            return redirect(url_for('catalog'))
    else:
        return render_template('addCategory.html')


@app.route('/catalog/<category_name>')
def showCategory(category_name):
    category = session.query(Category).filter_by(category_name = category_name).one()
    categories = session.query(Category).order_by(Category.category_name).all()
    items = session.query(Item).filter_by(category_id = category.category_id)
    return render_template('showCategory.html', category = category, categories = categories, items = items)


@app.route('/catalog/<category_name>/delete', methods = ['GET', 'POST'])
def deleteCategory(category_name):
    category = session.query(Category).filter_by(category_name = category_name).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash('Category and all its items deleted!')
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteCategory.html', category = category)


@app.route('/catalog/newitem', methods = ['GET', 'POST'])
def addItem():
    categories = session.query(Category).order_by(asc(Category.category_name))
    if request.method == 'POST':
        if request.form['item_name']:
            newItem = Item(item_name = request.form['item_name'],
                           item_description = request.form['item_description'],
                           item_price = request.form['item_price'],
                           category_id = request.form['category_id'])
            session.add(newItem)
            session.commit()
            category = session.query(Category).filter_by(category_id = newItem.category_id).one()
            flash('New Item added!')
            return redirect(url_for('showItem', category_name = category.category_name, item_name = newItem.item_name))
        else:
            flash('You did not add a new Item')
            return redirect(url_for('catalog'))
    else:
        return render_template('addItem.html', categories = categories)


@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(item_name = item_name).one()
    category = session.query(Category).filter_by(category_id = item.category_id).one()
    return render_template('showItem.html', item = item, category = category)


@app.route('/catalog/<category_name>/<item_name>/edit', methods = ['GET', 'POST'])
def editItem(category_name, item_name):
    item = session.query(Item).filter_by(item_name = item_name).one()
    category = session.query(Category).filter_by(category_id = item.category_id).one()
    categories = session.query(Category).order_by(Category.category_name).all()
    if request.method == 'POST':
        if request.form['item_name']:
            item.item_name = request.form['item_name']
        if request.form['item_description']:
            item.item_description = request.form['item_description']
        if request.form['item_price']:
            item.item_price = request.form['item_price']
        if request.form['category_id']:
            item.category_id = request.form['category_id']
        session.add(item)
        session.commit()
        editedCategory = session.query(Category).filter_by(category_id = item.category_id).one()
        flash("Item edited")
        return redirect(url_for('showItem', category_name = editedCategory.category_name, item_name = item.item_name))

    else:
        return render_template('editItem.html', item = item, category = category, categories = categories)


@app.route('/catalog/<category_name>/<item_name>/delete', methods = ['GET', 'POST'])
def deleteItem(category_name, item_name):
    category = session.query(Category).filter_by(category_name = category_name).one()
    item = session.query(Item).filter_by(item_name = item_name).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item deleted')
        return redirect(url_for('showCategory', category_name = category.category_name))
    else:
        return render_template('deleteItem.html', category = category, item = item)





#################
# API endpoints #
#################

# Create new user
@app.route('/api/users', methods = ['POST'])
def new_user():
    user_name = request.json.get('name')
    user_email = request.json.get('email')
    password = request.json.get('password')
    if user_name is None or password is None:
        return jsonify({"error":"Missing name and password arguments"})
        
    if session.query(User).filter_by(user_name = user_name).first() is not None:
        return jsonify({"message":"user already exists"})

    user = User(user_name = user_name, user_email = user_email)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ "username": user.user_name })


# Generate token for already logged in user
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({"token":token.decode('ascii')})


# Get all categories
@app.route('/api/catalog/categories')
def categories_handler():
    return getAllCategoriesAPI()


# Operate on a specific category
@app.route('/api/catalog/category', methods = ['GET', 'POST', 'PUT', 'DELETE'])
@auth.login_required
def category_handler():
    try:
        category_id = request.json.get('id')
        category_name = request.json.get('name')

        if category_id and request.method == 'GET':
            return getCategoryAPI(category_id)

        elif category_name and request.method == 'POST':
            return addCategoryAPI(category_name)
        
        elif category_id and category_name and request.method == 'PUT':
            return editCategoryAPI(category_id, category_name)

        elif request.method == 'DELETE':
            return deleteCategoryAPI(category_id)

        else:
            return jsonify({"error":"No valid key/value data for category request"})

    except:
        return jsonify({"error":"Cannot access Category ID %s" % category_id})


# Get all items
@app.route('/api/catalog/items')
def items_handler():
    try:
        items = session.query(Item).all()
        return getAllItemsAPI(items)

    except:
        return jsonify({"error":"Cannot retrive Items"})


# Operate on a specific item
@app.route('/api/catalog/item', methods = ['GET', 'POST', 'PUT', 'DELETE'])
@auth.login_required
def add_item_handler():
    try:
        category_id = request.json.get('category_id')
        item_id = request.json.get('id')
        item_name = request.json.get('name')
        item_price = request.json.get('price')
        item_description = request.json.get('description')

        # Retreiving an item with key: id
        if item_id and request.method == 'GET':
            return getItemAPI(item_id)

        # Creating new item with keys: category_id, name
        elif category_id and item_name and request.method == 'POST':
            return addItemAPI(category_id, item_name, item_price, item_description)

        # Editing item with key: id
        elif item_id and request.method == 'PUT':
            return editItemAPI(category_id, item_id, item_name, item_price, item_description)

        # Delete item with key: id
        elif item_id and request.method == 'DELETE':
            return deleteItemAPI(item_id)

        else:
            return jsonify({"error":"Cannot find relevant Key/Value pairs"})

    except:
        return jsonify({"error":"Invalid request, cannot operate on item"})


# Get all users info
@app.route('/api/catalog/users')
@auth.login_required
def users_handler():
    return getAllUsersAPI()



#############################
# Methods for API endpoints #
#############################

def getAllCategoriesAPI():
    try:
        categories = session.query(Category).all()
        if categories:
            return jsonify(categories = [i.serialize for i in categories])
        else:
            return jsonify({"error":"Cannot find any Categories"})
    except:
        return jsonify({"error":"Cannot retrive Categories"})


def getCategoryAPI(category_id):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        return jsonify(category = category.serialize)

    except:
        return jsonify({"error":"Cannot get category ID %s" % category_id})


def addCategoryAPI(category_name):
    try:
        category = session.query(Category).filter_by(category_name = category_name).one()
        return jsonify({"message":"Category %s already exists" % category_name})
            
    except NoResultFound:
        newCategory = Category(category_name = category_name)
        session.add(newCategory)
        session.commit()
        return jsonify(category = newCategory.serialize)


def editCategoryAPI(category_id, category_name):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        category.category_name = category_name
        session.add(category)
        session.commit()
        return jsonify(category = category.serialize)
    except:
        return jsonify({"error":"Cannot edit category ID %s" % category_id})


def deleteCategoryAPI(category_id):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        session.delete(category)
        session.commit()
        return jsonify({"message":"Category ID %s deleted" % category_id})

    except:
        return jsonify({"error":"cannot delete category ID %s" % category_id})


def getAllItemsAPI(items):
    if items:
        return jsonify(items = [i.serialize for i in items])
    else:
        return jsonify({"error":"Cannot find any Items"})


def getItemAPI(item_id):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        if item:
            return jsonify(item = item.serialize)
        else:
            return jsonify({"error":"Cannot find Item ID %s" % item_id})
    except:
        return jsonify({"error":"Cannot retrive Item ID %s" % item_id})


def addItemAPI(category_id, item_name, item_price, item_description):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        newItem = Item(category_id = category_id, item_name = item_name, item_price = item_price, item_description = item_description)
        session.add(newItem)
        session.commit()
        return jsonify(item = newItem.serialize)
    except:
        return jsonify({"error":"Category ID not valid: %s" % category_id})


def editItemAPI(category_id, item_id, item_name, item_price, item_description):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        if item and category_id:
            category = session.query(Category).filter_by(category_id = category_id).one()
            item.category_id = category_id
        if item and item_name:
            item.item_name = item_name
        if item and item_price:
            item.item_price = item_price
        if item and item_description:
            item.item_description = item_description
        session.add(item)
        session.commit()
        return jsonify(item = item.serialize)

    except:
        return jsonify({"error":"Not valid category or item ID"})


def deleteItemAPI(item_id):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        session.delete(item)
        session.commit()
        return jsonify({"message":"Deleted item with ID %s" % item_id})

    except:
        return jsonify({"error":"Cannot find item ID %s" % item_id})


def getAllUsersAPI():
    try:
        users = session.query(User).all()
        if users:
            return jsonify(users = [i.serialize for i in users])
        else:
            return jsonify({'error':'Cannot find any Users'})
    except:
        return jsonify({'error':'Cannot retrive Users'})




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host = '0.0.0.0', port = 8000, threaded = False)