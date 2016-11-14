# Wiki App
_______________

### Objective:

- create a 90s style wiki app where any user can edit and create pages. This was my second time creating a wiki app. The first time I created this app was as a pair programming session with Jesslyn Landgren.

### Live Demo

[Wiki App] (http://wikiapp.tech/)

### Languages used:

* HTML
* CSS
* Python
* Flask
* PyGreSQL
* Jinja
* PostGreSQL

### Authors:

Carolyn Lam

### Set Up Imports:

```
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, flash, render_template, redirect, request, session
import pg, markdown, time
from time import strftime, localtime
from wiki_linkify import wiki_linkify
import os

db = pg.DB(
    dbname=os.environ.get('PG_DBNAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('Wiki', template_folder=tmp_dir)
```

### Database Setup
```
CREATE TABLE page (
    id serial PRIMARY KEY,
    page_name varchar UNIQUE
);

CREATE TABLE page_content (
    id serial PRIMARY KEY,
    page_id integer REFERENCES page (id),
    content text,
    timestamp timestamp
);

CREATE TABLE user_auth (
  id serial PRIMARY KEY,
  username varchar UNIQUE,
  password varchar
);
```
