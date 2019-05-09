from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Puppy


engine = create_engine('sqlite:///puppies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
@app.route('/puppies', methods = ['GET', 'POST'])
def puppiesFunction():
    if request.method == 'GET':
        return getAllPuppies()
        
    elif request.method == 'POST':
        print 'Making a new puppy'
        name = request.args.get('name', '')
        description = request.args.get('description', '')
        print name
        print description
        return makeANewPuppy(name, description)


@app.route('/puppies/<int:id>', methods = ['GET', 'PUT', 'DELETE'])
def puppiesFunctionId(id):
    if request.method == 'GET':
        return getPuppy(id)
    
    elif request.method == 'PUT':
        name = request.args.get('name', '')
        description = request.args.get('description', '')
        return updatePuppy(id, name, description)

    elif request.method == 'DELETE':
        return deletePuppy(id)

def getAllPuppies():
    puppies = session.query(Puppy).all()
    return jsonify(Puppies=[i.serialize for i in puppies])


def getPuppy(id):
    puppy = session.query(Puppy).filter_by(id = id).one()
    return jsonify(puppy=puppy.serialize)


def makeANewPuppy(name, description):
    puppy = Puppy(name = name, description = description)
    session.add(puppy)
    session.commit()
    return jsonify(Puppy=puppy.serialize)


def updatePuppy(id, name, description):
    puppy = session.query(Puppy).filter_by(id = id).one()
    if not name:
        puppy.name = name
    if not description:
        puppy.description = description
    session.add(puppy)
    session.commit()
    return "Updated a puppy with id %s" % id


def deletePuppy(id):
    puppy = session.query(Puppy).filter_by(id = id).one()
    session.delete(puppy)
    session.commit()
    return "Removed puppy with id %s" % id


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000, threaded=False)