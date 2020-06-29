# mneme API [![Build Status](https://travis-ci.com/Mneme-org/API.svg?branch=master)](https://travis-ci.com/Mneme-org/API)

Written in [python](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/), it is at the heart of every mneme app, it is what lives in your server and manages your journals, 
essentially all other apps need to "talk" to it to get, create, or update your journals. It supports a minimum of python 3.7.

It's simple in use in case you want to create your own app that uses it.


## Road Map:
* [x] Create, delete, and update users
* [x] Create, delete, and update journals for users
* [x] Create, delete, and update entries for journals
* [x] Search function for keywords and dates
* [x] Read from config file
* [x] Only admin users can create accounts if the instance is private 
* [ ] Keep deleted entries for a while with option to delete instantly
* [ ] Way to reset password
* [ ] Export to text files and other formats?
* [ ] Allow attaching photos or other files as well?
* [ ] Optional PostgreSQL database instead of SQLite?

## Installation:
```shell script
$ git clone https://github.com/Mneme-org/API.git mneme-api
$ cd mneme-api
$ cp example_config.ini config.ini
# Edit config.ini as needed 

# You can either install with poetry:
$ poetry install
$ poetry run python run.py

# Or if you don't have/want poetry you can use pip:
$ pip install -r requirements.txt
$ python run.py
```


 ### License
 This project is licensed under the GPLv3 License. See the [LICENSE](https://github.com/Mneme-org/mneme-server/blob/master/LICENSE) file for the full license text.
