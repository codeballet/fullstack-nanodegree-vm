import httplib2
import json

def getGeocodeLocation(inputString):
    google_api_key = 'AIzaSyCs59EEuNsQ3wrkqNlP3ZDc5XNql-_ss3g'
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (
        locationString, google_api_key))
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content)
    # print "response header: %s \n \n" % response
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return (latitude, longitude)
