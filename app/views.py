from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import User
from app.forms import LoginForm

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')

@app.route('/after_login')
def after_login():
    # this netid
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)

    user = User.query.filter_by(netid=login).first()
    if user is None:
        nickname = login
        user = User(nickname=nickname, email=nickname+"@rice.edu")
        db.session.add(user)
        db.session.commit()

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return app.send_static_file('intro.html') #temporarily redirecting user to intro page, TODO: figure out logic post-login

@app.route('/')
def index():
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = {'nickname': login}
    return app.send_static_file('intro.html')

@app.route('/about')
def about():
    return app.send_static_file('about.html')
	
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
