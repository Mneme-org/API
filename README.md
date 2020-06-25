# mneme API [![Build Status](https://travis-ci.com/Mneme-org/API.svg?branch=master)](https://travis-ci.com/Mneme-org/API)

Written in [Python](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/), the API is at the heart of every mneme setup, and lives in your server and manages your journals, entries, and user. The front-end apps communicate with this API, and can handle any of the work, so it seems seamless for the end user. Minimum Python version is 3.7, though it is possible to use 3.6 if you install `async-exit-stack` and `async-generator` as dependencies.

The API can easily be used, so you could even make your own front-end app, or submit pull-requests or issues to ours!

## Features:
* Create, delete, and update users
* Create, delete, and update journals for users
* Create, delete, and update entries for journals
* Search function for keywords and dates
* Optional Encryption (This is actually taken care of in the front end)

## To do:
* Way to reset password
* Export to text files and other formats
* Allow attaching photos or other files as well
* Keep deleted entries for a while with option to delete instantly
* Optional PostgreSQL database instead of SQLite

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
 
 ### Special Thanks
 A special thank you to everyone in the Discord_Bots discord server for assisting is in an uncountable amount of ways, again, thank you!
