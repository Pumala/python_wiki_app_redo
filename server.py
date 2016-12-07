from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, flash, render_template, redirect, request, session
import pg, markdown, time
from time import strftime, localtime
from wiki_linkify import wiki_linkify
import os

db = pg.DB(
    dbname=os.environ.get('PG_DB_NAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)

# App Secret key
app.secret_key = os.environ.get("SECRET_KEY")

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('Wiki', template_folder=tmp_dir)

@app.route('/')
def render_homepage():
    count = session.get('count', 0)
    session['count'] = count + 1

    return render_template(
        'homepage.html'
    )

@app.route('/<page_name>')
def render_page_name(page_name):

    # make a query to grab all the data for the value of page_name
    query = db.query("select page_content.content, page.id as page_id, page_content.id as content_id from page, page_content where page.id = page_content.page_id and page.page_name = $1 order by page_content.id desc limit 1", page_name)
    wiki_page = query.namedresult()

    # set has_content and page_is_taken to False initially
    has_content = False
    page_is_taken = False

    # check the length of the query to see if an entry for it exists in the db
    if len(wiki_page) < 1:
        # if it doesn't exist, set content to an empty string
        content = ""
    else:
        # if it does exist, set page_is_taken to True
        page_is_taken = True
        # assign content the value of content from the query
        content = wiki_page[0].content
    # check the length of content to see if there's any content
    if len(content) > 0:
        # if so, assign the value of True
        has_content = True
    else:
        # else, keep has_content as False and move on
        pass
    # use markdown and wiki_linkify to update the content
    content = markdown.markdown(wiki_linkify(content))

    return render_template(
        'pageholder.html',
        page_is_taken = page_is_taken,
        page_name = page_name,
        markdown = markdown,
        wiki_linkify = wiki_linkify,
        has_content = has_content,
        content = content
    )

@app.route('/<page_name>/edit')
def render_page_edit(page_name):
    # first check if the user is logged in
    if 'username' in session:
        # if so, proceed and make a query to grab the content
        query = db.query("select page_content.content from page, page_content where page.id = page_content.page_id and page.page_name = $1 order by page_content.id desc limit 1", page_name)
        wiki_page = query.namedresult()
        # check the length of the query
        if len(wiki_page) > 0:
            # if there's content, assign it to content
            content = wiki_page[0].content
        else:
            # if there isn't, assign it an empty string value
            content = ""
        return render_template(
            'edit_page.html',
            page_name = page_name,
            content = content
        )
    else:
        # if user isn't logged in, redirect back to the page
        return redirect('/%s' % page_name)

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

@app.route('/search', methods=['POST'])
def redirect_search():
    # grab the value of the search keyword
    search = request.form.get('search')
    # redirect to that search keyword page
    return redirect('/%s' % search)

@app.route('/<page_name>/history')
def view_page_history(page_name):
    # make a query to grab all the timestamp, id, and content associated with a particular page
    query = db.query("select page_content.timestamp, page_content.id from page, page_content where page.id = page_content.page_id and page.page_name = $1", page_name)
    page_histories = query.namedresult()

    return render_template(
        'page_history.html',
        page_name = page_name,
        page_histories = page_histories
    )

@app.route('/<page_name>/history/record')
def view_page_record(page_name):
    # grab the content id
    content_id = request.args.get('id')
    # make a query to select a specific timestamp, and content from a page
    query = db.query("select page_content.content, page_content.timestamp from page, page_content where page.id = page_content.page_id and page_content.id = $1", content_id)
    page_record = query.namedresult()[0]

    return render_template(
        'page_record.html',
        page_name = page_name,
        page_record = page_record
    )

@app.route('/all_pages')
def list_all_pages():
    # make a querk to grab all the pages that exist in the db
    query = db.query('select page_name from page')
    all_pages = query.namedresult()
    return render_template(
        'all_pages.html',
        all_pages = all_pages
    )

@app.route('/register')
def new_register():
    return render_template(
        'register.html'
    )

@app.route('/submit_register_form', methods=['POST'])
def submit_new_user_auth():
    # grab the username and password values that the new user submitted
    username = request.form.get('username')
    password = request.form.get('password')
    # create a new entry in user_auth table in db
    db.insert(
        'user_auth', {
            'username': username,
            'password': password
        }
    )
    # log the user
    session['username'] = username
    # flash a message letting the user know they have successfully signed up
    flash('You have successfully signed up $1!', username)
    return redirect('/')

@app.route('/login')
def login_user():
    return render_template(
        'login.html'
    )

@app.route('/submit_login', methods=['POST'])
def is_logged_in():
    # grab the username and password values
    username = request.form.get('username')
    password = request.form.get('password')

    # make a query to grab everything connected to the username
    query = db.query("select * from user_auth where username = $1", username)
    user_info = query.namedresult()
    print "USER INFO: %r" % user_info
    # check the length of the query result
    # if it's greater than 0, then the user is already a member
    if len(user_info) > 0:
        # we check if the passwords match
        if user_info[0].password == password:
            # if so, the user is logged in
            session['username'] = username
            # display a message informing the user of being logged in
            flash('You have successfully logged in %s!' % username)
            # redirect back to home page
            return redirect('/')
    else:
        pass
    # redirect back to login route if user does not exist or passwords did not match
    return redirect('/login')

@app.route('/logout')
def logout_user():
    username = session['username']
    # logs the user out of their session
    del session['username']
    # display a message letting user know they are logged out
    flash('You have successfully logged out %s!' % username)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
