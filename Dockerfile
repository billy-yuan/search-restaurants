# syntax=docker/dockerfile:1

FROM python:3.8

# make directory
# RUN mkdir /search-restaurants

# set working directory
WORKDIR /

# copy requirements to working directory
COPY requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# copy source code to working directory
COPY . .

# make downloads folder
RUN mkdir search_service/download

# run server
CMD uvicorn api.app:app --host=0.0.0.0 --port=${PORT:-8000}


