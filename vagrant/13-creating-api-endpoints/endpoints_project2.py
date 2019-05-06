from flask import Flask, request
app = Flask(__name__)


@app.route('/puppies', methods=['GET', 'POST'])
def puppiesFunction():
    if request.method == 'GET':
        return getAllPuppies()

    elif request.method == 'POST':
        return makeANewPuppy()

@app.route('/puppies/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def puppiesFunctionID(id):
    if request.method == 'GET':
        return getPuppy(id)

    if request.method == 'PUT':
        return updatePuppy(id)

    elif request.method == 'DELETE':
        return deletePuppy(id)


def getAllPuppies():
    return "Getting All the puppies!"

def makeANewPuppy():
    return "Creating a new puppy!"

def getPuppy(id):
    return "Getting puppy with id %s" % id

def updatePuppy(id):
    return "Updating puppy with id %s" % id

def deletePuppy(id):
    return "Removing Puppy with id %s" % id
    
if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5000)