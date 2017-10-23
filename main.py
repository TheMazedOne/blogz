from flask import Flask, request, render_template, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, \
     check_password_hash
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:deadlands@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = """I’ve always been impulsive. My thinking is usually pretty good, but I always seem to do it after I do my talking—by"""

class Blog(db.Model):
    
    id=db.Column( db.Integer, primary_key=True)
    title = db.Column( db.String(277))
    post = db.Column(db.Text)
    owner_id=db.Column( db.Integer, db.ForeignKey( 'user.id'))
    date_posted = db.Column(db.DateTime)    
    
    def __init__(self,title,post, owner, date_posted):
        self.title = title
        self.post = post
        self.owner = owner
        self.date_posted = date_posted

class User(db.Model):
    id=db.Column( db.Integer, primary_key=True)
    username=db.Column(db.String(77))
    password=db.Column(db.String(777))
    blogs=db.relationship('Blog',backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, loggedin=check_logged_in(session))

def check_logged_in( session ):
    if 'username' in session:
        return True
    return False

@app.before_request
def logged_in():
    unlocked = [ 'index', 'login', 'register', 'blog' ]

    if request.endpoint not in unlocked and not check_logged_in( session ):
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form["user_name"]
        password = request.form["password"]

        user = User.query.filter_by( username=username ).first()

        if user and password == user.password:
            session['username'] = user.username
            return redirect('/blog?user='+str(user.id))
        else:
            user_error = " This username and password are not a thing! "
            return render_template('login.html', user_error=user_error)
        
    return render_template('login.html', loggedin=check_logged_in(session))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        
        username = request.form["user_name"]
        password = request.form["password"]
        vpassword = request.form["vpassword"]

        username_error = valid( username )
        password_error = valid( password )
        vpassword_error = ''

        if password != vpassword: 
            vpassword_error = "Passwords do not match"

        if not username_error and not password_error and not vpassword_error:
            existing_user = User.query.filter_by( username=username ).first()
            
            if not existing_user:
                newuser = User(username, password)
                db.session.add( newuser )
                db.session.commit()

                session['username'] = newuser.username

                return redirect('/blog?user='+str(newuser.id))
            else:
                username_error = "This username already IS!"
                return render_template('register.html',  loggedin=check_logged_in(session),user_name = form_username, 
            user_error = username_error)

        return render_template('register.html',  loggedin=check_logged_in(session),
    user_name = username, user_error = username_error, password_error = password_error, 
    vpassword_error = vpassword_error)        
    return render_template('register.html', loggedin=check_logged_in(session))

@app.route('/blog')
def blog():    
    get_post_id = request.args.get('id')
    get_user_id = request.args.get('user')
    posts = Blog.query.order_by(Blog.date_posted.desc()).all()
    date_posted = Blog.date_posted

    if get_post_id:
        post_id = int(get_post_id)
        user_post = Blog.query.get( post_id )

        if user_post:
            return render_template('post.html', loggedin=check_logged_in(session), posts=user_post)
        else:
            return render_template('newp.html', loggedin=check_logged_in(session))
    
    
    if get_user_id:
        user = User.query.get( int(get_user_id) )
        posts = user.blogs
        


    return render_template('/blog.html', loggedin=check_logged_in(session),posts=posts)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == "POST":
        title_title = request.form['title_title']
        post_post = request.form['post_post']
         
        title_error= "" "" 
        post_error = "" ""

        if not title_title: 
            title_error = "Needs a Title!"
        if not post_post: post_error = "Fill This Post!"

        if not title_error and not post_error:
            owner = User.query.filter_by( username = session['username'] ).first()
            date_posted=datetime.now()
            new_post = Blog(title_title, post_post, owner, date_posted)
            db.session.add(new_post)
            db.session.commit()

            return redirect('/blog?id='+str(new_post.id) )

        else:
            return render_template('/newpost.html', loggedin=check_loggedin(session),
        title_error=title_error, post_error=post_error,title=title_title,post=post_post)

    return render_template('/newpost.html', loggedin=check_logged_in(session))

def valid( item ):
    message = ''
    if len(item)<3 or len(item)>20 or ' ' in item:
        message = "Must be between 3-20 characters and no spaces."
    return message

@app.route('/logout')
def logout():
    del session['username']
    flash("You Escaped!")
    return redirect('/')


if __name__=="__main__":
    app.run()