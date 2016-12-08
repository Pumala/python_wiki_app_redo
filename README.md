# Wiki App
_______________

### Objective:

- create a 90s style wiki app where any logged in user can edit and create pages

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

### Code Samples:

* Below is a code sample from the back-end
* This post method happens when a user has made changes to a page
* the logic checks if the page exists as an entry in the db
* if not, it creates a new entry
* then it updates the content for that page in the db

```
@app.route('/<page_name>/save', methods=['POST'])
def save_page_edit(page_name):
    # grab the new content from the user
    content = request.form.get('content')
    # check if 'page_name' exists in the database
    query = db.query("select page_content.content, page.id as page_id, page_content.id as content_id from page, page_content where page.id = page_content.page_id and page.page_name = $1 order by page_content.id desc limit 1", page_name)
    result = query.namedresult()
    # if it doesn't exist, create a new page in the database
    if len(result) < 1:
        db.insert(
            'page', {
                'page_name': page_name
            }
        )
    else:
        pass
    # now that we're certain that the page exists in the database, we again grab the query
    # and insert new content in the database
    query = db.query("select id from page where page_name = $1", page_name)
    page_id = query.namedresult()[0].id
    db.insert(
        'page_content', {
            'page_id': page_id,
            'content': content,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", localtime())
        }
    )
    return redirect("/%s" % page_name)
```

* below is code sample from the front-end (dynamic pageholder page)
* it uses the jinja template to render the content being passed from the back-end
* certain parts of the code display depending on this content
* for instance, session['username'] checks if the user is logged in
* if so, it renders the following code
* else, it does not render the code

```
{% extends 'homepage.html' %}

{% block body %}
  <h1>{{page_name}}</h1>
  {% if has_content %}
    <div class="content-div">
      <p>
        {{content | safe }}
      </p>
    </div>
  <div class="links-div">
    {% if session['username'] %}
    <a href="/{{page_name}}/edit">Edit Content</a>
    {% else %}
    <div class="login_register">
      <p>
        Please
        <a href="/login">login</a>
        or
        <a href="/register">register</a>
        to edit the content.
      </p>
    </div>
    {% endif %}
    <a href="/{{page_name}}/history">View Page History</a>
  </div>
  {% else %}
    <div class="content-div">
      <p>
        This page has not been created.
      </p>
    </div>
    {% if session['username'] %}
    <div class="create_content">
      <a class="block-level" href="/{{page_name}}/edit">Create New Content</a>
    </div>
    {% else %}
    <div class="login_register">
      <p>
        Please
        <a href="/login">login</a>
        or
        <a href="/register">register</a>
        to create new content.
      </p>
    </div>
    {% endif %}
  {% endif %}
{% endblock %}

```
