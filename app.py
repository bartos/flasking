from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
import sqlite3


# configuration
DATABASE = 'tasker.db'
DEBUG = True
SECRET_KEY = 'secret_key_1'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    """ Connects to db"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def create_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    db=get_db()
    cur = db.execute('select * from entries order by id desc')
    entries = cur.fetchall()
    return render_template('index.html',entries=entries)


@app.route('/login', methods=['GET','POST'])
def login():
    """USER session management"""
    error=None
    
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:            
            error="wrong username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'wrong password'
        else:
            session['logged_in']=True
            flash('you were logged in')
            return redirect(url_for('index'))
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """ user logout management"""
    session.pop('logged_in',None)
    flash('you were logged out')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """Add new post to database."""
    if not session.get('logged_in'):
        print("Abort401")
        abort(401)
    db = get_db()
    
    db.execute(
        'insert into entries (title, text) values (?, ?)',
        [request.form['title'], request.form['text']]
    )
    db.commit()
    flash('New entry was successfully posted')    
    return redirect(url_for('index'))

@app.route('/delete/<post_id>',methods=['GET'])
def delete_entry(post_id):
    result = {'status': 0, 'message': 'Error'}
    if not session.get('logged_in'):
        # result = {'status': 2, 'message': 'Only logged in users can delete posts.'}
        abort(401)
    try:
        db = get_db()
        db.execute('delete from entries where id='+post_id)
        db.commit()
        result = {'status': 1, 'message':'Post deleted'}
    except Exception as e:
        result = {'status': 0, 'message':repr(e)}
    return jsonify(result)

if __name__=="__main__":
    create_db()
    app.run()
    

