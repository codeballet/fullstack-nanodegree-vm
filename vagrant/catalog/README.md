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

## Loggin in options
On the HTML web interface, the only option for logging in is by means of Google's OAuth 2.0 service. To log in and register as a user, simply click on the Google `Sign In` button on the `http://localhost:8000/login` page.


## Contributions
The software is created as part of the Udacity course "Full Stack Web Developer Nanodegree Program". Hence, it is a stricly limited study in SQL and Python programming and is currently not open to contributions.

## Licensing
The intellectual property of all code is owned by Johan Stjernholm. For licensing rights of the database content and all other external tools and dependencies, please see the licensing rights of each provider.
