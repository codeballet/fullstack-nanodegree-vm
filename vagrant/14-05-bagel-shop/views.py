from models import Base, User, Bagel
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth() 


engine = create_engine('sqlite:///bagelShop.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

#ADD @auth.verify_password here
@auth.verify_password
def verify_password(username, password):
    print 'Looking for user %s' % username
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        print 'user %s not verified' % username
        return False
    else:
        print 'password verified'
        g.user = user
        return True


#ADD a /users route here
@app.route('/users', methods = ['POST'])
def addUser():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print 'missing arguments'
        abort(400)
    
    if session.query(User).filter_by(username = username).first() is not None:
        print 'existing user'
        return jsonify({'message':'user already exists'})

    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username})


#protect this route with a required login
@app.route('/bagels', methods = ['GET','POST'])
@auth.login_required
def showAllBagels():
    print 'inside showAllBagels, login passed'
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels = [bagel.serialize for bagel in bagels])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        newBagel = Bagel(name = name, description = description, picture = picture, price = price)
        session.add(newBagel)
        session.commit()
        return jsonify(newBagel.serialize)



if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000, threaded = False)