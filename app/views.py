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
    # Fields from form
    fields = ["net_id", "name", "year", "age", "college", "gender", "bio"]
    # User-entered values from form
    values = []
    for field in fields:
        values.append(request.form[field])
    # Complain if the user left one of the fields blank (excluding the optional bio)
    if "" in values[:6]:
        # raise an error and stop
        pass
    # Create a new user from the Profile model
    user = Profile(values[0], values[1], values[2], values[3], values[4], values[5], values[6])
    # Add this new user to the databsae
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
    return Profile.query.get(int(id))
