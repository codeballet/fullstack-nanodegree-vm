from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from model import Category, User, Item, Base


app = Flask(__name__)
engine = create_engine('sqlite:///antiques.db')
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()





##############
# HTML views #
##############

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

@app.route('/api/catalog/items')
def items_handler():
    return getAllItems()


@app.route('/api/catalog/category/<category_id>/item/new', methods = ['GET', 'POST'])
def add_item_handler(category_id):
    try:
        category = session.query(Category).filter_by(category_id = category_id).first()
        if category != None and request.method == 'POST':
            item_name = request.args.get('name')
            item_description = request.args.get('description')
            item_price = request.args.get('price')
            return addItem(category.category_id, item_name, item_description, item_price)
        else:
            return jsonify({'error':'Cannot find category, check your category ID'})
    except:
        return jsonify({'error':'Invalid request, check your category ID'})


@app.route('/api/catalog/item/<int:item_id>', methods = ['GET', 'PUT', 'DELETE'])
def item_handler(item_id):
    try:
        if request.method == 'GET':
            print 'Getting an Item'
            return getItem(item_id)

        elif request.method == 'PUT':
            print 'Editing an Item'
            item_id = request.args.get('id')
            item_name = request.args.get('name')
            item_description = request.args.get('description')
            item_price = request.args.get('price')
            return editItem(item_id, item_name, item_description, item_price)
        
        elif request.method == 'DELETE':
            print 'Deleting an Item'
            return deleteItem(item_id)
    except:
            return jsonify({'error':'Invalid request'})


@app.route('/api/catalog/categories')
def categories_handler():
    return getAllCategories()


@app.route('/api/catalog/users')
def users_handler():
    return getAllUsers()



##################################
# Methods for database retreival #
##################################

def getAllItems():
    try:
        items = session.query(Item).all()
        if items:
            return jsonify(items = [i.serialize for i in items])
        else:
            return jsonify({'error':'Cannot find any Items'})
    except:
        return jsonify({'error':'Cannot retrive Items'})


def getItem(item_id):
    try:
        item = session.query(Item).filter_by(item_id = item_id).one()
        if item:
            return jsonify(item = item.serialize)
        else:
            return jsonify({'error':'Cannot find the Item'})
    except:
        return jsonify({'error':'Cannot retrive the Item'})


def addItem(category_id, item_name, item_description, item_price):
    try:
        if item_name:
            newItem = Item(
                category_id = category_id,
                item_name = item_name,
                item_description = item_description,
                item_price = item_price
            )
            session.add(newItem)
            session.commit()
            return jsonify(item = newItem.serialize)
        else:
            return jsonify({'error':'Missing Item name argument'})
    except:
        return jsonify({'error':'Cannot create Item'})


def getAllCategories():
    try:
        categories = session.query(Category).all()
        if categories:
            return jsonify(categories = [i.serialize for i in categories])
        else:
            return jsonify({'error':'Cannot find any Categories'})
    except:
        return jsonify({'error':'Cannot retrive Categories'})


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