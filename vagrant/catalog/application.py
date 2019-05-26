from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from model import Category, User, Item, Base


app = Flask(__name__)
engine = create_engine('sqlite:///antiques.db')
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()





##################
# HTML endpoints #
##################

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

@app.route('/api/catalog/categories')
def categories_handler():
    return getAllCategories()


@app.route('/api/catalog/category', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def category_handler():
    try:
        category_id = request.json.get('id')
        category_name = request.json.get('name')

        if category_id and request.method == 'GET':
            return getCategory(category_id)

        elif category_name and request.method == 'POST':
            return addCategory(category_name)
        
        elif category_id and category_name and request.method == 'PUT':
            return editCategory(category_id, category_name)

        elif request.method == 'DELETE':
            return deleteCategory(category_id)

        else:
            return jsonify({"error":"No valid key/value data for category request"})

    except:
        return jsonify({"error":"Cannot access Category ID %s" % category_id})


@app.route('/api/catalog/items')
def items_handler():
    try:
        items = session.query(Item).all()
        return getAllItems(items)

    except:
        return jsonify({"error":"Cannot retrive Items"})


@app.route('/api/catalog/item', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def add_item_handler():
    try:
        category_id = request.json.get('category_id')
        item_id = request.json.get('id')
        item_name = request.json.get('name')
        item_price = request.json.get('price')
        item_description = request.json.get('description')

        # Retreiving an item with key: id
        if item_id and request.method == 'GET':
            return getItem(item_id)

        # Creating new item with keys: category_id, name
        elif category_id and item_name and request.method == 'POST':
            return addItem(category_id, item_name, item_price, item_description)

        # Editing item with key: id
        elif item_id and request.method == 'PUT':
            return editItem(category_id, item_id, item_name, item_price, item_description)

        # Delete item with key: id
        elif item_id and request.method == 'DELETE':
            return deleteItem(item_id)

        else:
            return jsonify({"error":"Cannot find relevant Key/Value pairs"})

    except:
        return jsonify({"error":"Invalid request, cannot operate on item"})


@app.route('/api/catalog/users')
def users_handler():
    return getAllUsers()



#############################
# Methods for API endpoints #
#############################

def getAllCategories():
    try:
        categories = session.query(Category).all()
        if categories:
            return jsonify(categories = [i.serialize for i in categories])
        else:
            return jsonify({"error":"Cannot find any Categories"})
    except:
        return jsonify({"error":"Cannot retrive Categories"})


def getCategory(category_id):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        return jsonify(category = category.serialize)

    except:
        return jsonify({"error":"Cannot get category ID %s" % category_id})


def addCategory(category_name):
    try:
        category = session.query(Category).filter_by(category_name = category_name).one()
        return jsonify({"message":"Category %s already exists" % category_name})
            
    except NoResultFound:
        newCategory = Category(category_name = category_name)
        session.add(newCategory)
        session.commit()
        return jsonify(category = newCategory.serialize)


def editCategory(category_id, category_name):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        category.category_name = category_name
        session.add(category)
        session.commit()
        return jsonify(category = category.serialize)
    except:
        return jsonify({"error":"Cannot edit category ID %s" % category_id})


def deleteCategory(category_id):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        session.delete(category)
        session.commit()
        return jsonify({"message":"Category ID %s deleted" % category_id})

    except:
        return jsonify({"error":"cannot delete category ID %s" % category_id})


def getAllItems(items):
    if items:
        return jsonify(items = [i.serialize for i in items])
    else:
        return jsonify({"error":"Cannot find any Items"})


def getItem(item_id):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        if item:
            return jsonify(item = item.serialize)
        else:
            return jsonify({"error":"Cannot find Item ID %s" % item_id})
    except:
        return jsonify({"error":"Cannot retrive Item ID %s" % item_id})


def addItem(category_id, item_name, item_price, item_description):
    try:
        category = session.query(Category).filter_by(category_id = category_id).one()
        newItem = Item(category_id = category_id, item_name = item_name, item_price = item_price, item_description = item_description)
        session.add(newItem)
        session.commit()
        return jsonify(item = newItem.serialize)
    except:
        return jsonify({"error":"Category ID not valid: %s" % category_id})


def editItem(category_id, item_id, item_name, item_price, item_description):
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


def deleteItem(item_id):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        session.delete(item)
        session.commit()
        return jsonify({"message":"Deleted item with ID %s" % item_id})

    except:
        return jsonify({"error":"Cannot find item ID %s" % item_id})


def getAllUsers():
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