from findARestaurant import findARestaurant
from models import Base, Restaurant
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

engine = create_engine('sqlite:///restaurants.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/restaurants', methods = ['GET', 'POST'])
def all_restaurants_handler():
    if request.method == 'GET':
        return getAllRestaurants()

    elif request.method == 'POST':
        print 'Creating new restaurant'
        location = request.args.get('location')
        mealType = request.args.get('mealType')
        print 'location: %s' % location
        print 'mealType: %s' % mealType
        return createRestaurant(location, mealType)


@app.route('/restaurants/<int:id>', methods = ['GET', 'PUT', 'DELETE'])
def restaurant_handler(id):
    if request.method == 'GET':
        print 'Getting a restaurant'
        return getRestaurant(id)

    elif request.method == 'PUT':
        print 'Updating a restaurant'
        name = request.args.get('name')
        location = request.args.get('location')
        image = request.args.get('image')
        return updateRestaurant(id, name, location, image)
    
    elif request.method == 'DELETE':
        print 'Deleting a restaurant'
        return deleteRestaurant(id)


@app.route('/restaurants/deleteall', methods = ['GET', 'DELETE'])
def deleteall_handler():
    if request.method == 'DELETE':
        print 'Deleting all restaurants'
        return deleteAll()


def getAllRestaurants():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants = [i.serialize for i in restaurants])


def createRestaurant(location, mealType):
    print 'inside createRestaurant'
    try:
        restaurant_info = findARestaurant(location, mealType)
        if restaurant_info != 'No Restaurants Found':
            print 'restaurant info: %s' % unicode(restaurant_info)
            newRestaurant = Restaurant(
                restaurant_name = unicode(restaurant_info['name']),
                restaurant_address = unicode(restaurant_info['address']),
                restaurant_image = restaurant_info['image']
            )
            session.add(newRestaurant)
            session.commit()
            return jsonify(restaurant = newRestaurant.serialize)
        else:
            return jsonify({'error':'No Restaurants returned for %s in %s' % (mealType, location)})
    except:
        return jsonify({'error':'Cannot retrive Restaurants for %s in %s' % (mealType, location)})



def getRestaurant(id):
    try:
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        if restaurant:
            return jsonify(restaurant = restaurant.serialize)
        else:
            return jsonify({'error':'No restaurant found for id %s' % id})
    except:
        return jsonify({'error':'Cannot retrieve restaurant for id %s' % id})


def updateRestaurant(id, name, location, image):
    try:
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        if restaurant:
            if name:
                restaurant.restaurant_name = name
            if address:
                restaurant.restaurant_address = location
            if image:
                restaurant.restaurant_image = image
            session.add(restaurant)
            session.commit()
            return jsonify(restaurant = restaurant.serialize)
        else:
            return jsonify({'error':'Cannot find restaurant id %s' % id})
    except:
        return jsonify({'error':'Cannot retrieve restaurant id %s' % id})


def deleteRestaurant(id):
    try:
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        if restaurant:
            session.delete(restaurant)
            session.commit()
            return jsonify({'message':'Deleted restaurant id %s' % id})
        else:
            return jsonify({'error':'Cannot find restaurant id %s' % id})
    except:
            return jsonify({'error':'Cannot retrieve restaurant id %s' % id})


def deleteAll():
    restaurants = session.query(Restaurant).all()
    print 'found restaurants: %s' % restaurants
    for restaurant in restaurants:
        session.delete(restaurant)
        session.commit()
    return jsonify({'message':'Deleted all restaurants'})


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
