# -*- coding: utf-8 -*-
import httplib2
import json

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

foursquare_client_id = "BDQ0GSXBHBLXKCWO3NRSS2WC0QN1YJXCM3ARUTAB5V20WMDZ"
foursquare_client_secret = "QXQJFZWDKL2NVBUDFB1RCL0QIGFHBTZRKXZIHAQCWWRNZHZO"
google_api_key = 'AIzaSyCs59EEuNsQ3wrkqNlP3ZDc5XNql-_ss3g'


# Function takes a location string and returns geolocation from googleapi
def getGeocodeLocation(inputString):
    # Replace spaces with '+' in URL
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


# Function gets restaurant infor from Foursquare
def findARestaurant(location, mealType):
    #1. Use getGeocodeLocation to get the latitude and longitude coordinates of the location string.
    latitude, longitude = getGeocodeLocation(location)
	
	#2.  Use foursquare API to find a nearby restaurant with the latitude, longitude, and mealType strings.
	#HINT: format for url will be something like https://api.foursquare.com/v2/venues/search?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815&ll=40.7,-74&query=sushi
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20180323&ll=%s,%s&query=%s' % (
        foursquare_client_id, foursquare_client_secret, latitude, longitude, mealType))
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    data = json.loads(content)

    if data['response']['venues']:
        #3. Grab the first restaurant
        restaurant = data['response']['venues'][0]
        restaurant_id = restaurant['id']
        restaurant_name = restaurant['name']
        restaurant_address = restaurant['location']['formattedAddress']
        address = ''
        for i in restaurant_address:
            address += i + ' '
        restaurant_address = address

        #4. Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
        url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&client_secret=%s&v=20180323' % (
            restaurant_id, foursquare_client_id, foursquare_client_secret))
        h = httplib2.Http()
        response, content = h.request(url, 'GET')
        data = json.loads(content)
        if data['response']['photos']['items']:
        #5. Grab the first image
            photo = data['response']['photos']['items'][0]
            prefix = photo['prefix']
            suffix = photo['suffix']
            image_url = prefix + '300x300' + suffix
        else:
            #6. If no image is available, insert default a image url
            image_url = 'https://pixabay.com/photos/hamburger-food-meal-tasty-dining-494706/'
        
        #7. Return a dictionary containing the restaurant name, address, and image url
        restaurant_info = {'name': restaurant_name, 'address': restaurant_address, 'image': image_url}
        # print 'Restaurant name: %s' % restaurant_info['name']
        # print 'Restaurant address: %s' % restaurant_info['address']
        # print 'Restaurant image: %s\n' % restaurant_info['image']
        return restaurant_info
    else:
        return 'No Restaurants Found'


if __name__ == '__main__':
    findARestaurant("Pizza", "Tokyo, Japan")
    findARestaurant("Tacos", "Jakarta, Indonesia")
    findARestaurant("Tapas", "Maputo, Mozambique")
    findARestaurant("Falafel", "Cairo, Egypt")
    findARestaurant("Spaghetti", "New Delhi, India")
    findARestaurant("Cappuccino", "Geneva, Switzerland")
    findARestaurant("Sushi", "Los Angeles, California")
    findARestaurant("Steak", "La Paz, Bolivia")
    findARestaurant("Gyros", "Sydney, Australia")