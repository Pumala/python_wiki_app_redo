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
from flask import Flask, render_template, redirect, request
import pg, markdown, time
from time import strftime, localtime
from wiki_linkify import wiki_linkify

app = Flask('WikiApp')

db = pg.DB(dbname='wiki_db_redo')
```
