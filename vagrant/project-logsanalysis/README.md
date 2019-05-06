# Logs analysis

The program `logs_analysis.py` collects data from a PostgreSQL database called 'news'. The program makes SQL queries, extracting the following information:
* The three most popular articles all time.
* The most popular authors all time.
* Days where the request fault rate is more than 1%.

## Installation and configuration
To run the program, you may ssh into a virtual machine, pre-configured in a Vagrant file. To do so, you first need to install the following software:
* [Git](https://git-scm.com/downloads)
* [Virtualbox](https://www.virtualbox.org/)
* [Vagrant](https://www.vagrantup.com/)

To get the Vagrant configuration file of the Virtual Machine, fork and clone the following repository:
* https://github.com/udacity/fullstack-nanodegree-vm

Inside the cloned directory, there is a `vagrant` directory. Change directory to that `vagrant` directory and run the command `vagrant up`.
Once the virtual machine configuration has finished its work, you may connect via SSH to the virtual machine with the command `vagrant ssh`.
When you see a shell prompt starting with the word `vagrant`, you have successfully logged into the virtual machine.

Inside the virtual machine, change to the `/vagrant` directory. That directory is shared with the folder / directory called `vagrant` in the cloned folder / directory of your host operative system.

Now you need to download the data that will populate the database from here:
* [newsdata.sql](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)

Unzip the downloaded file and put `newsdata.sql` in the `/vagrant` directory that is shared between your virtual machine and host operative system. To load the data, `cd` into that same `/vagrant` directory and use the command `psql -d news -f newsdata.sql`.

You should now have a database called `news` that is populated with data from the file `newsdata.sql`.

In addition to the pre-configured dependencies in your Vagrant virtual machine, `logs_analysis.py` requires the PostgreSQL adapter `psycopg2`. You can install it with the command:
* `pip install psycopg2`

To finally use the program `logs_analysis.py`, download and put that file into your shared `/vagrant` directory. To run the program, use the command:
`python logs_analysis.py`

You may verify the correctness of the code by comparing the output to the content of the textfile `logs_analysis.txt`.

### Full list of requirements
In case you do not want to use the preconfigured Vagrant file and Virtualbox, the full list of dependencies are:
```
bleach==3.1.0
certifi==2019.3.9
chardet==3.0.4
Click==7.0
Flask==1.0.2
Flask-HTTPAuth==3.2.4
Flask-SQLAlchemy==2.3.2
httplib2==0.12.1
idna==2.8
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.1
oauth2client==4.1.3
packaging==19.0
passlib==1.7.1
psycopg2-binary==2.7.7
pyasn1==0.4.5
pyasn1-modules==0.2.4
pyparsing==2.3.1
redis==3.2.1
requests==2.21.0
rsa==4.0
six==1.12.0
SQLAlchemy==1.3.1
urllib3==1.24.1
webencodings==0.5.1
Werkzeug==0.15.1
```
To install all the above requirements, copy the above list into a file called `requirements.txt` and run the command `pip install -r requirements.txt`

The program requires Python version 3.

## Options
The program has the option to automatically generate a text file output of the collected data. To enable the text file output, simply uncomment the lines immediately under the comments:
`# OPTIONAL - generate text file with log output`

There is one optional text file output section that can be enabled under each of the three main functions:
* `pop_art()`
* `pop_auth()`
* `error_days()`

## Contributions
The software is created as part of the Udacity course "Full Stack Web Developer Nanodegree Program". Hence, it is a stricly limited study in SQL and Python programming and is currently not open to contributions.

## Licensing
The intellectual property of all code is owned by Johan Stjernholm. For licensing rights of the database content and all other external tools and dependencies, please see the licensing rights of each provider.
