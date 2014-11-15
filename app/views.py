from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import Profile
from app.forms import LoginForm

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')

@app.route('/after_login', methods=['GET'])
def after_login():
    # User Net ID
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)

    # Dictionary of values to pass
    data = {"net_id": login}

    # Try to find Net ID in database
    user = Profile.query.filter_by(net_id=login).first()
    if user is None:
        # User doesn't exist in DB
        # Redirect the user to the profile creation page
        print("User does not exist")
        return render_template('profile_creation.html', data=data)
    else:
        # User does exist in DB
        # Redirect user to main page
        print("User does exist")
        return app.send_static_file('intro.html')

@app.route('/createprofile', methods=['POST'])
def create_user():
    """
    Processes form data in POST request and adds the user to the database table Profiles.
    """
    net_id = request.form['net_id']
    name = request.form['name']
    year = request.form['year']
    age = request.form['age']
    college = request.form['college']
    gender = request.form['gender']
    bio = request.form['bio']
    user = Profile(net_id, name, year, age, college, gender, bio)
    db.session.add(user)
    db.session.commit()
    return app.send_static_file('intro.html')

@app.route('/', methods=['GET'])
def index():
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = {'nickname': login}
    return app.send_static_file('intro.html')


@app.route('/about')
def about():
    return app.send_static_file('about.html')


@lm.user_loader
def load_user(id):
    return Profiles.query.get(int(id))
