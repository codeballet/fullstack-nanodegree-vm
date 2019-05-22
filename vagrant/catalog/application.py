from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from model import Category, User, Item, Base


app = Flask(__name__)
engine = create_engine('sqlite:///antiques.db')
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()




@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).order_by(asc(Category.category_name))
    items = session.query(Item).order_by(desc(Item.item_date)).limit(10)
    list_categories = []
    for item in items:
        get_category = session.query(Category).filter_by(category_id = item.category_id).one()
        list_categories.append(get_category.category_name)
    return render_template('catalog.html', categories = categories, items = items, list_categories = list_categories)


@app.route('/catalog/category/new', methods = ['GET', 'POST'])
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
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id = category.category_id)
    return render_template('showCategory.html', category = category, categories = categories, items = items)


@app.route('/catalog/item/new', methods = ['GET', 'POST'])
def addItem():
    categories = session.query(Category).order_by(Category.category_name).all()
    if not categories and request.method == 'POST':
        if request.form['item_name'] and request.form['category_name']:
            newCategory = Category(category_name = request.form['category_name'])
            session.add(newCategory)
            session.commit()
            addedCategory = session.query(Category).first()
            newItem = Item(item_name = request.form['item_name'],
                           item_description = request.form['item_description'],
                           item_price = request.form['item_price'],
                           category_id = addedCategory.category_id)
            session.add(newItem)
            session.commit()
            flash('New Item added!')
            return redirect(url_for('catalog'))
        else:
            flash('You did not add a new Item')
            return redirect(url_for('catalog'))

    elif request.method == 'POST':
        if request.form['item_name']:
            newItem = Item(item_name = request.form['item_name'],
                           item_description = request.form['item_description'],
                           item_price = request.form['item_price'],
                           category_id = request.form['category_id'])
            session.add(newItem)
            session.commit()
            flash('New Item added!')
            return redirect(url_for('catalog'))
        else:
            flash('You did not add a new Item')
            return redirect(url_for('catalog'))
    elif not categories and request.method == 'GET':
        return render_template('addCategoryItem.html')
    else:
        return render_template('addItem.html', categories = categories)


@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
    print 'in the showItem view'
    item = session.query(Item).filter_by(item_name = item_name).one()
    print 'item name: %s' % item.item_name
    category = session.query(Category).filter_by(category_id = item.category_id).one()
    return render_template('showItem.html', item = item, category = category)


@app.route('/catalog/<category_name>/<item_name>/edit', methods = ['GET', 'POST'])
def editItem(category_name, item_name):
    editedItem = session.query(Item).filter_by(item_name = item_name).one()
    category = session.query(Category).filter_by(category_id = editedItem.category_id).one()
    categories = session.query(Category).order_by(Category.category_name)
    if request.method == 'POST':
        if request.form['item_name']:
            editedItem.item_name = request.form['item_name']
            editedItem.item_description = request.form['item_description']
            editedItem.item_price = request.form['item_price']
            editedItem.category_id = request.form['category_id']
            session.add(editedItem)
            session.commit()
            editedCategory = session.query(Category).filter_by(category_id = editedItem.category_id).one()
            flash('Item "{{ editedItem.item_name }}" edited')
            return render_template('showItem.html', category_name = editedCategory.category_name, item_name = editedItem.item_name)
        else:
            flash('Please edit all the fields!')
            return redirect(url_for('editItem', category_name = category.category_name, item_name = item.item_name))

    else:
        return render_template('editedItem.html', item = editedItem, category = category, categories = categories)


@app.route('/catalog/<category_name>/<item_name>/delete', methods = ['GET', 'POST'])
def deleteItem(category_name, item_name):
    return 'here you delete an item'



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host = '0.0.0.0', port = 8000, threaded = False)