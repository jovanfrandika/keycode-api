FROM python:3.8.1-slim-buster

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app

EXPOSE 4000
CMD ["gunicorn", "-b", "0.0.0.0:4000", "app:app"]
