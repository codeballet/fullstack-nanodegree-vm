from flask import Flask, render_template, request, redirect, url_for, jsonify,\
    flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem


app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()


@app.route('/restaurants/JSON/')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [r.serialize for r in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def showMenuJSON(restaurant_id):
    menuItems = session.query(MenuItem)\
        .filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems = [i.serialize for i in menuItems])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def showMenuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem = menuItem.serialize)


@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)


@app.route('/restaurant/new/', methods = ['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name']:
            newRestaurant = Restaurant(name = request.form['name'])
            session.add(newRestaurant)
            session.commit()
            flash('New restaurant created!')
            return redirect(url_for('showRestaurants'))
        else:
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            flash('Restaurant successfully edited!')
            return redirect(url_for('showRestaurants'))
        else:
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant = restaurant)



@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('Restaurant successfully deleted!')
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurant)



@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return render_template('menu.html',
        restaurant = restaurant,
        items = items)


@app.route('/restaurant/<int:restaurant_id>/menu/new/',
    methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],
                           description = request.form['description'],
                           price = request.form['price'],
                           course = request.form['course'],
                           restaurant_id = restaurant.id)
        session.add(newItem)
        session.commit()
        flash('Menu item created!')
        return redirect(url_for('showMenu', restaurant_id = restaurant.id))
    else:
        return render_template('newMenuItem.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/',
    methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        item.course = request.form['course']
        session.add(item)
        session.commit()
        flash('Menu item successfully edited!')
        return redirect(url_for('showMenu', restaurant_id = restaurant.id))
    else:
        return render_template('editMenuItem.html',
            restaurant = restaurant,
            item = item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/',
    methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Menu item successfully deleted!')
        return redirect(url_for('showMenu', restaurant_id = restaurant.id))
    else:
        return render_template('deleteMenuItem.html',
            restaurant = restaurant,
            item = item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host = '0.0.0.0', port = 5000)
