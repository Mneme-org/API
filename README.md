# mneme API [![Build Status](https://travis-ci.com/Mneme-org/API.svg?branch=master)](https://travis-ci.com/Mneme-org/API)

Written in [Python](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/), the API is at the heart of every mneme setup, and lives in your server to manage your journals, entries, and user. The front-end apps communicate with this API, making it a seamless experience for the end user. Minimum Python version is 3.7.

The API can easily be used, so you could even make your own front-end app, or submit pull-requests or issues to ours!


## Road Map:
* [x] Create, delete, and update users
* [x] Create, delete, and update journals for users
* [x] Create, delete, and update entries for journals
* [x] Search function for keywords and dates
* [x] Read from config file
* [x] Only admin users can create accounts if the instance is private 
* [x] Keep deleted entries and journals for a while with option to delete instantly
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

$ pip install -r requirements.txt
$ python ./mnemeapi.py
```
 
 ## Special Thanks
 A special thank you to everyone in the Discord_Bots discord server for assisting is in an uncountable amount of ways, again, thank you!
 
 
 ### License
 This project is licensed under the GPLv3 License. See the [LICENSE](https://github.com/Mneme-org/mneme-server/blob/master/LICENSE) file for the full license text.
