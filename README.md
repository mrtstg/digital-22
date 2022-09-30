# DigitalSkillsApp

App which lets you manage schedules!

## About

App uses PostgreSQL 14.5 for storage and can be configured with `.env` files, app was tested on Ubuntu 22.04.

### Run

To run app locally you need to:  
- create database;
- fill `.env` file with your values;
- create venv by using `make venv`;
- database user must have enough privileges to run migrations on specified database (create tables, alter table, etc);
- apply migrations by using `make migrate`;
- database user must have enough privileges to work with specified database (select, insert, update, delete);
- use `make run`.

### Testing

Be careful! 
Tests are designed to create and drop specified database!

The coverage is pretty low, but we got login, add user and delete user tests.

To run tests locally you need to:
- fill `.env.test` file with your values;
- create venv by using `make venv`;
- database user must have enough privileges to create and drop databases during tests;
- use `make tests`;

### Cleanup

You can delete venv and all `*.pyc` files by using `make clean`

### Productions

To deploy an app to production environment you need to:
- create new virtual environment (`python -m venv /path/to/your/venv`) or use existing;
- activate it by using `source /path/to/your/venv/bin/activate`;
- install requirements by using `pip install -r requirements.txt`
- export environmental variables by using `set -a; . ./.env`
- run migrations by using `alembic upgrade head`
- walk to source directory using `cd ./source`
- run app by using `python main.py`

Application runs using uvicorn (ASGI web-server), so, you need to configure any web-server to work as reverse proxy to serve it.
For example, you can configure Nginx and use proxy_pass.

Minimal nginx config example:
```
server {
    listen 80;
    server_name digital39.test;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        add_header 'Access-Control-Allow-Credentials' 'true';
    }
}

```


### Usage
You need to log in to manage users, teachers, courses and lessons.

Default credentials (added doing migrations):
- username: `admin`
- password:`P@ssw0rd`

You can change password in Users menu.

Also, you can:
- add/remove users;
- add/remove teachers;
- add/remove courses;
- add/remove lessons from schedule;

### For CI/CD

Differences between `master` and `dev`:
 - Title of webpage changed from `DigitalSkills` to `DigitalSkillsTest` in `base.html`, line 9.
 - Logo changed from `DigitalSkills` to `DigitalSkillsTest` in `base.html`, line 15.

To break tests you can change any assert with `== 200` in test files to `!= 200`.
For example, change line 17 in `tests/test_login.py`

If you want to commit some safe code you can change title in `base.html` for example or just add a new line anywhere to create some changes.

### Build & basic deploy

```
cd digital-22
docker build -t app .
```

```
docker run -p 80:8000 -d app --name app
```
