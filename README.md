# Starnavi_test_task

Test task: Python Developer. Social Network, simple REST API.

### Basics

1. Fork/Clone
1. Activate a virtualenv
1. Install the requirements

### Set Environment Variables

Create *.env* file in project's root directory and add following:

SECRET_KEY=\x80H\x16m6\xf6VE;\xc0T\x8ez\xbc\xff,#\xf2\xb6\x0f\xc5\x19\xd4
POSTGRES_LOCAL_BASE=postgresql://'user':'password'@'host':'port'/

Generate your SECRET_KEY using ```python os.urandom()```

### Create DB

Create the databases in `psql`:

```sh
$ psql
# create database flask_jwt_auth
# create database flask_jwt_auth_test
# \q
```

Create the tables and run the migrations:

```sh
$ python manage.py create_db
$ python manage.py db init
$ python manage.py db migrate
```
### Testing

```sh
$ python manage.py test
```

### Run the Application

```sh
$ python manage.py runserver
```
Access the application at the address [http://localhost:5000/](http://localhost:5000/)


### Implemented Functionality

- User Registration 

- User Login
 
- Post Creation

- Post Like

- Post Unlike

- Analytics about how many likes was made aggregated by day

- Information about users last activities (last login and request)

#### User Registration

- request type : POST
- endpoint : '/auth/register'
- request body: ```{'email'='joe@gmail.com','password'='123456'}```
- response: ```{
    "message": "Successfully registered.",
    "status": "success"
}```

#### User Login

- request type : POST
- endpoint :  '/auth/login'
- request body: ```{'email'='joe@gmail.com', 'password'='123456'}```
- response: ```{
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDEyODI2MDQsImlhdCI6MTYwMTI4MDgwNCwic3ViIjo0fQ.FNtKLU2TsArvh0FJIT9KjWyQJvZyijr7GqcJ9ef9N6c",
    "message": "Successfully logged in.",
    "status": "success"
}```

#### Post Creation

- request type : POST
- endpoint : '/post/create'
- request body: ```{ 'post_text'='Hello, this is my new post'} ```
- response: ```{
    "message": "Added new post.",
    "status": "success"
}```

#### Post Like/Unlike

- request type : POST
- endpoint : /post/like-unlike
- request body: ```{'post_id'='1'}```
- response: ```{
    "message": "Post liked/disliked",
    "status": "success"
}```

#### Analytics about how many likes was made aggregated by day

- request type : GET
- endpoint : api/analitics/?date_from=yyyy-mm-dd&date_to=yyyy-mm-dd
- response: ```{
    "likes_counter": 2,
    "status": "success"
}```

#### Information about users last activities (last login and request)

- request type : GET
- endpoint : /api/status/<int:user_id>
- response: ```{
    "data": {
        "last_login": "Mon, 28 Sep 2020 11:21:12 GMT",
        "last_request": "Sun, 27 Sep 2020 11:37:43 GMT"
    },
    "status": "success"
}```





