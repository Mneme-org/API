#!/bin/bash

poetry run uvicorn api.main:app --reload
