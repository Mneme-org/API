#!/bin/bash

poetry run uvicorn server.api.main:app --reload
