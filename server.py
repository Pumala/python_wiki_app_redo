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

@app.route('/')
def render_homepage():
    count = session.get('count', 0)
    session['count'] = count + 1

    return render_template(
        'homepage.html'
    )

@app.route('/<page_name>')
def render_page_name(page_name):
    query = db.query("select page_content.content, page.id as page_id, page_content.id as content_id from page, page_content where page.id = page_content.page_id and page.page_name = $1 order by page_content.id desc limit 1", page_name)
    wiki_page = query.namedresult()
    has_content = False
    page_is_taken = False
    if len(wiki_page) < 1:
        content = ""
    else:
        page_is_taken = True
        content = wiki_page[0].content
    if len(content) > 0:
        has_content = True
    else:
        pass
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
    if 'username' in session:
        query = db.query("select page_content.content from page, page_content where page.id = page_content.page_id and page.page_name = $1 order by page_content.id desc limit 1", page_name)
        wiki_page = query.namedresult()
        if len(wiki_page) > 0:
            content = wiki_page[0].content
        else:
            content = ""
        return render_template(
            'edit_page.html',
            page_name = page_name,
            content = content
        )
    else:
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
    search = request.form.get('search')
    return redirect('/%s' % search)

@app.route('/<page_name>/history')
def view_page_history(page_name):
    query = db.query("select page_content.timestamp, page_content.id from page, page_content where page.id = page_content.page_id and page.page_name = $1", page_name)
    page_histories = query.namedresult()

    return render_template(
        'page_history.html',
        page_name = page_name,
        page_histories = page_histories
    )

@app.route('/<page_name>/history/record')
def view_page_record(page_name):
    content_id = request.args.get('id')
    query = db.query("select page_content.content, page_content.timestamp from page, page_content where page.id = page_content.page_id and page_content.id = $1", content_id)
    page_record = query.namedresult()[0]

    return render_template(
        'page_record.html',
        page_name = page_name,
        page_record = page_record
    )

@app.route('/all_pages')
def list_all_pages():
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
    username = request.form.get('username')
    password = request.form.get('password')
    db.insert(
        'user_auth', {
            'username': username,
            'password': password
        }
    )
    session['username'] = username
    flash('You have successfully signed up %s!' % username)
    return redirect('/')

@app.route('/login')
def login_user():
    return render_template(
        'login.html'
    )

@app.route('/submit_login', methods=['POST'])
def is_logged_in():
    username = request.form.get('username')
    password = request.form.get('password')

    query = db.query("select * from user_auth where username = $1", username)
    user_info = query.namedresult()
    print "USER INFO: %r" % user_info
    if len(user_info) > 0:
        if user_info[0].password == password:
            session['username'] = username
            flash('You have successfully logged in %s!' % username)
            return redirect('/')
    else:
        pass
    return redirect('/login')

@app.route('/logout')
def logout_user():
    username = session['username']
    del session['username']
    flash('You have successfully logged out %s!' % username)
    return redirect('/')


app.secret_key = 'tell your mama that you will be home with bubbly'

if __name__ == '__main__':
    app.run(debug=True)
