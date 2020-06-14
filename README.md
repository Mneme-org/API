# mneme-server [![Build Status](https://travis-ci.org/Mneme-org/mneme-server.svg?branch=master)](https://travis-ci.org/Mneme-org/mneme-server)

The main mneme app is split in two parts. The web-app that you can use to access your journals from everywhere
and the API. The web-app and the native apps "talk" to the API.

So the design of mneme is very modular, you could create your own web or native apps that have the api at their core 
if you wanted.

---

The web app is not developed at all for now (contributions are welcome) and we don't have a plan for it yet
as none of us has made something like it before.

---

The [API](https://github.com/Mneme-org/mneme-server/tree/master/server/api) for mneme is made with [python](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/)
and it supports a minimum of python 3.7 (however it's possible to make it work with python 3.6 if you install a couple more dependencies, namely `async-exit-stack` and `async-generator`). 
