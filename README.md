# WireGuy

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Development

```bash
# we are using poetry for dependency management
poetry install
poetry shell

# run once to create database
PYTHONPATH=. python helpers/db_create.py

# run app in for developement in virtual env
FLASK_APP=wireguy.web FLASK_ENV=development flask run
# or
SECRET_KEY=abc python -m wireguy
```


## Deployment

```shell
docker-compose build
# first run, later it should just connect to existing db
docker-compose run web python3 helpers/db_create.py
docker-compose up
```

### Caution

This: `-v /etc/localtime:/etc/localtime:ro` is required to match the timezone in the container to timezone of the host

### Envvars

[`SECRET_KEY`](https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key#22463969) in .env