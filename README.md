# Wiki App

##### *Objective*: Create a 90s style wiki - where any user can edit and create pages

### Set up Imports

```
from flask import Flask, render_template, redirect, request
import pg, markdown, time
from time import strftime, localtime
from wiki_linkify import wiki_linkify

app = Flask('WikiApp')

db = pg.DB(dbname='wiki_db_redo')
```
