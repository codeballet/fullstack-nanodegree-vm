# Item catalog

The *Item Catalog* is a full-stack web app with a HTML interface and an API. The web app allows for loggin in as a registered user. Once logged in, the user can add, edit, and delete categories, as well as items for each category. Non-logged in users can still browse and access all items and categories, but they cannot edit, delete, or add new categories or items. 

## Installation and configuration
To run the program, you can ssh into a virtual machine, which is pre-configured in a Vagrant file. To do so, you first need to install the following software:
* [Git](https://git-scm.com/downloads)
* [Virtualbox](https://www.virtualbox.org/)
* [Vagrant](https://www.vagrantup.com/)

To get the Vagrant configuration file of the Virtual Machine, fork and clone the following repository:
* https://github.com/udacity/fullstack-nanodegree-vm

Inside the cloned directory, there is a `vagrant` directory. Change directory to that `vagrant` directory and run the command `vagrant up`.
Once the virtual machine configuration has finished its work, you may connect via SSH to the virtual machine with the command `vagrant ssh`.
When you see a shell prompt starting with the word `vagrant`, you have successfully logged into the virtual machine.

Inside the virtual machine, change directory to `/vagrant`. That directory is shared with the folder / directory called `vagrant` in the cloned folder / directory of your host operative system. Also inside the `/vagrant` directory, download or clone the files in the following repository:
* (http address for 'item-catalog' here...)

To start the server, change directory to the `item-catalog` and run `python application.py`. The server should now be running, and the list of categores available at `http://localhost:8000/` and `http://localhost:8000/catalog`.

### Requirements
In case you do not want to use the preconfigured Vagrant file and Virtualbox, all dependencies are listed in the file `requirements.txt`. To install all the requirements in your own configuration, run the command `pip install -r requirements.txt`

## Loggin in on the HTML website
### Create a new user and login on the webpage
On the HTML web interface, the only option for logging in is by means of Google's OAuth 2.0 service. To log in and register as a user on the `http://localhost:8000/login` page, simply click on the Google `Sign In` button.

In case you have never logged on before, a new user will be created, collecting your Google user account name and email information. Once logged on, the website will display a welcome page that includes a temporary token, which you may use to access the API.

## Using the API
### Creating new user and login with the API
To access the API, you may use a tool such as `curl`. To create a new user, you need to submit a `name`, `email`, and `password` to the API endpoint `/api/users`. For instance:
```
curl -H "Content-Type: application/json" -d '{"name":"your_name","email":"email@email.com","password":"your_password"}' http://localhost:8000/api/users
```
Having created a user, you may access the API, providing the `name` and `password` information. Altearnatively, you may use the temporary token displayed at the HTML login page, upon a successful OAuth login.

### API Resources available without login
There are three API endpoints available for a non-logged in user:
* `/api/users` to create new users (as above).
* `/api/catalog/categories` to get a json response with all existing categories in the database.
* `/api/catalog/items` to get a json response with all existing items in the database.

For instance, you may acquire all categories like so:
```
curl http://localhost:8000/api/catalog/categories
```

### API calls as a logged in user
You may log in with username and password, such as `curl -u name:password`. Alternatively, you may use a temporary token. The token can be acquired in two ways.

The first way to acquire a temporary token is to login on the HTML webpage, using the Google Sign in button. Upon logging in, a temporary token will be displayed on the successful login page.

The second way is to create a user account over the API (as described above), and then send a request to the `/api/token` endpoint. For instance:
```
curl -u your_name:your_password http://localhost:8000/api/token
```
The json response will contain a token as such:
```
{"token":"some_token_code"}
```
ONce the token is received, it may be used for further requests, instead of entering the username and password. When using a token, you enter the token in the place of the `name` field, and any value may be entered in the the password field, for instance `curl -u your_token:blank`.

### Operating on categories with the API
As a logged in user, you may view any category. You may add new categies, and you may edit and delete your own categores. The API endpoint for operating on categories is:
```
/api/catalog/category
```
#### Adding a category with `POST`
To add a category, you need to send a `POST` request to the above API endpoint. The request must have a category `name` specified. For instance:
```
 curl -X POST -H "Content-Type: application/json" -u name:password -d '{"name":"Category_name"}' http://localhost:8000/api/catalog/category
```
#### Viewing a category with `GET`
In order to view a category, you need to send a `GET` request with the category `id` of the relevant category, such as:
```
curl -X GET -H "Content-Type: application/json" -u name:password -d '{"id":"1"}' http://localhost:8000/api/catalog/category
```
#### Editing a category with `PUT`
To edit a category, you send a `PUT` request, containing the category `id` and `name`. For instance:
```
 curl -X PUT -H "Content-Type: application/json" -u name:password -d '{"id":"1","name":"New_category_name"}' http://localhost:8000/api/catalog/category
```
#### Deleting a category with `DELETE`
To delete a category, you send a `DELETE` request, containing the category `id`, such as:
```
 curl -X DELETE -H "Content-Type: application/json" -u name:password -d '{"id":"1"}' http://localhost:8000/api/catalog/category
```

### Operating on items with the API
As a logged in user, you may view any item in the database. You may also create, edit, and delete items in your own categories. You may not create, edit, or delete items in other users categories.

The API endpoint for operating on items is:
```
/api/catalog/item
```
#### Adding an item to a category with `POST`
To add an item to a category, you send a `POST` request. The request must contain the following data:
* `category_id` for the category you want the item to belong to.
* `name` of the item.
You may only add items to your own categories.

Optional pieces of information that may be provided about the item are:
* `price`
* `description` giving more details about the item.
The request may look like this:
```
curl -X POST -H "Content-Type: application/json" -u name:password -d '{"category_id":"1","name":"Item name","price":"Some price","description":"Some description"}' http://localhost:8000/api/catalog/item
```
#### Viewing an item with `GET`
To view an item, your own or an item belonging to another user, you may send a `GET` request with the relevant item `id`. Example of request:
```
curl -X GET -H "Content-Type: application/json" -u name:password -d '{"id":"1"}' http://localhost:8000/api/catalog/item
```
#### Editing an item with `PUT`
To edit an item, you send a `PUT` 



## Contributions
The software is created as part of the Udacity course "Full Stack Web Developer Nanodegree Program". Hence, it is a stricly limited study in SQL and Python programming and is currently not open to contributions.

## Licensing
The intellectual property of all code is owned by Johan Stjernholm. For licensing rights of the database content and all other external tools and dependencies, please see the licensing rights of each provider.
