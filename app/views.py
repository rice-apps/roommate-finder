from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import Profile
from app.forms import LoginForm
from werkzeug.utils import secure_filename
import os, random

# This needs to be an absolute path. That's so stupid.
UPLOAD_FOLDER = "C:/Users/Kevin/SkyDrive/Homework/Rice University/Miscellaneous/Rice Apps/roommate-finder/app/photos"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    Processes form data in POST request from profile creation page and adds the user to the database table Profile.

    The profile photo associated with the user is recorded in the column "photo" in the Profile table.
    It is stored as <hash>.<file_extension> where <hash> is a hash is a hash of the uploaded photo and <file_extension> is...well, the file extension.
    The actual photo file is stored as app/photos/<hash>.<file_extension>
    """
    # Fields from form
    fields = ["net_id", "name", "year", "age", "college", "gender", "bio"]
    # Get user-entered values from form
    values = []
    for field in fields:
        values.append(request.form[field])
    # Uploaded profile photo
    photo = request.files['photo']
    # Generate a string representation of a hash of the photo
    # This associates the local copy of the file with the user in the database
    photo_hash = str(hash(photo))
    # Create a new user from the Profile model
    if photo:
        user = Profile(values[0], values[1], values[2], values[3], values[4], values[5], values[6], photo_hash + "." + file_extension(photo.filename))
    else:
        user = Profile(values[0], values[1], values[2], values[3], values[4], values[5], values[6])
    # Add this new user to the database
    db.session.add(user)
    db.session.commit()
    # Store the user's profile photo on the server
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo_hash) + "." + file_extension(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return app.send_static_file('intro.html')


def allowed_file(filename):
    """
    Check if the file if of a permissible file extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def file_extension(file):
    """
    Get the file extension of file. Excludes the "." before the extension.
    """
    return file.rsplit('.', 1)[1]


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
