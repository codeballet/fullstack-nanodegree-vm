from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
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
    categories = session.query(Category).all()
    return render_template('catalog.html', categories = categories)


@app.route('/catalog/new', methods = ['GET', 'POST'])
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


@app.route('/catalog/<category_name>/new', methods = ['GET', 'POST'])
def addItem(category_name):
    if request.method == 'POST':
        category = session.query(Category).filter_by(category_name = category_name).one()
        if request.form['item_name']:
            newItem = Item(item_name = request.form['item_name'],
                           item_desciption = request.form['item_description'],
                           item_price = request.form['item_price'],
                           category_id = category.category_id)
            session.add(newItem)
            session.commit()
            flash('New Item added!')
            return redirect(url_for('showCategory', category_name = category.category_name))
        else:
            flash('You did not add a new Item')
            return redirect(url_for('showCategory', category_name = category.category_name))
    else:
        return render_template('addItem', category = category)


@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
    return 'here are details about an item'


@app.route('/catalog/<category_name>/<item_name>/edit', methods = ['GET', 'POST'])
def editItem(category_name, item_name):
    return 'here you edit an item'


@app.route('/catalog/<category_name>/<item_name>/delete', methods = ['GET', 'POST'])
def deleteItem(category_name, item_name):
    return 'here you delete an item'



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host = '0.0.0.0', port = 8000, threaded = False)