#!/bin/bash

poetry shell
pwd
uvicorn server.api.main:app --reload
