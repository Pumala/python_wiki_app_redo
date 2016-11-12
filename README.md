# Wiki App
_______________

### Objective:

- create a 90s style wiki - where any user can edit and create pages

### Live Demo

....

### Languages used:

* HTML
* CSS
* Python
* Flask

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
