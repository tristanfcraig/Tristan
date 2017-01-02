import sqlite3

from flask import Flask, request, make_response, redirect, render_template, url_for, session, g, abort, flash
from flask_mail import Mail, Message
from contextlib import closing


DATABASE = '/tmp/tristan.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'tristanfcraig'
PASSWORD = 'Isadora321.'

app = Flask(__name__)
app.config.from_object(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'contact.tristanfcraig@gmail.com'
app.config['MAIL_PASSWORD'] = 'Isadora321.'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    about1 = g.db.execute('select id, name, mission from groups order by id desc')
    groups = [dict(id=row[0], name=row[1], mission=row[2]) for row in about1.fetchall()]
    about2 = g.db.execute('select id, author, quote, context_url from quotes order by id desc')
    quotes = [dict(id=row[0], author=row[1], quote=row[2], context_url=row[3]) for row in about2.fetchall()]
    return render_template('about.html', groups=groups, quotes=quotes)


@app.route("/projects")
def projects():
    project_list = g.db.execute('select id, name, image_url, description from projects order by id desc')
    projects = [dict(id=row[0], name=row[1], image_url=row[2], description=row[3]) for row in project_list.fetchall()]
    return render_template('projects.html', projects=projects)

@app.route("/blog")
def blog():
    blog = g.db.execute('select id, title, medium_url, content from posts order by id desc')
    posts = [dict(id=row[0], title=row[1], medium_url=row[2], content=row[3]) for row in blog.fetchall()]
    return render_template('blog.html', posts=posts)

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "GET":

        return render_template("contact.html")

    else:

        if not request.form.get("first_name"):
            return render_template('apology.html')

        if not request.form.get("last_name"):
            return render_template('apology.html')

        if not request.form.get("email"):
            return render_template('apology.html')

        if not request.form.get("message"):
            return render_template('apology.html')

        msg = Message('Message from ' + request.form.get("first_name") + ' ' + request.form.get("last_name") + ' (' + request.form.get("email") + ')', sender = request.form.get("email"), recipients = ['tcraig@college.harvard.edu'])
        msg.body = request.form.get("message")
        mail.send(msg)

        return redirect(url_for("index"))

@app.route('/add_quote', methods=['GET', 'POST'])
def add_quote():
    if not session.get('logged_in'):
        abort(401)

    if request.method == 'GET':
        return render_template("add_quote.html")

    else:
        g.db.execute('insert into quotes (author, quote, context_url) values (?, ?, ?)',
            [request.form.get('author'), request.form.get('quote'), request.form.get('context_url')])
        g.db.commit()
        flash('New quote was successfully added')
        return redirect(url_for('about'))

@app.route('/delete_quote', methods=['POST'])
def delete_quote():
    if not session.get('logged_in'):
        abort(401)

    else:
        g.db.execute('delete from quotes where id = ?',
            [request.form.get("quote_id")])
        g.db.commit()
        flash('Quote was successfully deleted')
        return redirect(url_for('about'))

@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
    if not session.get('logged_in'):
        abort(401)

    if request.method == 'GET':
        return render_template("add_group.html")

    else:
        g.db.execute('insert into groups (name, mission) values (?, ?)',
            [request.form.get('name'), request.form.get('mission')])
        g.db.commit()
        flash('New group was successfully added')
        return redirect(url_for('about'))

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if not session.get('logged_in'):
        abort(401)

    if request.method == 'GET':
        return render_template("add_project.html")

    else:
        g.db.execute('insert into projects (name, image_url, description) values (?, ?, ?)',
            [request.form.get('name'), request.form.get('url'), request.form.get('description')])
        g.db.commit()
        flash('New project was successfully added')
        return redirect(url_for('projects'))

@app.route('/delete_project', methods=['POST'])
def delete_project():
    if not session.get('logged_in'):
        abort(401)

    else:
        g.db.execute('delete from projects where id = ?',
            [request.form.get("project_id")])
        g.db.commit()
        flash('Project was successfully deleted')
        return redirect(url_for('projects'))

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)

    if request.method == 'GET':
        return render_template("add_post.html")

    else:
        g.db.execute('insert into posts (title, medium_url, content) values (?, ?, ?)',
            [request.form.get('title'), request.form.get('url'), request.form.get('content')])
        g.db.commit()
        flash('New post was successfully added')
        return redirect(url_for('blog'))

@app.route('/delete_post', methods=['POST'])
def delete_post():
    if not session.get('logged_in'):
        abort(401)

    else:
        g.db.execute('delete from posts where id = ?',
            [request.form.get("post_id")])
        g.db.commit()
        flash('Post was successfully deleted')
        return redirect(url_for('blog'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)
