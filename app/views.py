from flask import render_template, flash, redirect, session, url_for, request, g, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import Profile
from app.forms import LoginForm
from werkzeug.utils import secure_filename
import os, random, urllib2

# This needs to be an absolute path. That's so stupid.
UPLOAD_FOLDER = "C:/Users/Kevin/SkyDrive/Homework/Rice University/Miscellaneous/Rice Apps/roommate-finder/app/photos"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')


@app.route('/photos/<path:filename>')
def photos(filename):
    """
    Proper routing of /photos, the uploaded profile pictures directory.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


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
        # Get user details from Rice public directory
        (name, year, college) = get_user_details(login)
        data["name"] = name
        data["year"] = year
        data["college"] = college
        # Redirect the user to the profile creation page
        return render_template('profile_creation.html', data=data)
    else:
        # User does exist in DB
        # Redirect user to main page
        data["profile"] = user
        return render_template('my_profile.html', data=data)


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
    data = {"net_id": values[0], "profile": user}
    return render_template('my_profile.html', data=data)


@app.route('/updateprofile', methods=['POST'])
def update_user():
    """
    Called when the user is modifying is/her account from the My Profile page.
    Updates the database to reflect the user's changes.
    """
    # Retrieve the user by net ID from the database
    user = Profile.query.filter_by(net_id=request.form["net_id"]).first()
    # Update all the columns
    user.name = request.form["name"]
    user.year = request.form["year"]
    user.age = request.form["age"]
    user.college = request.form["college"]
    user.gender = request.form["gender"]
    user.bio = request.form["bio"]
    # Update the photo only if the user has changed the picture
    photo = request.files['photo']
    if photo and allowed_file(photo.filename):
        photo_hash = str(hash(request.files['photo']))
        filename = secure_filename(photo_hash) + "." + file_extension(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.photo = photo_hash + "." + file_extension(photo.filename)
    # Commit the changes
    db.session.merge(user)
    db.session.commit()
    # Pass along the data after refresh
    data = {"net_id": user.net_id, "profile": user}
    return render_template('my_profile.html', data=data)


@app.route('/deleteprofile', methods=['GET', 'POST'])
def delete_user():
    """
    Removes the user from the database.
    """
    # Get Net ID from GET data
    net_id = request.args.get('net_id', '')
    # Security measure - make sure the Net ID of the user whose deletion was requested
    # matches with the Net ID of the user currently logged in
    # This is a pretty lame security measure in all truth
    if session.get(app.config['CAS_USERNAME_SESSION_KEY'], None) == net_id:
        user = Profile.query.filter_by(net_id=net_id).first()
        db.session.delete(user)
        db.session.commit()
    return app.send_static_file('intro.html')


def get_user_details(net_id):
    """
    Look up the passed net ID in the Rice online directory and attempt to find
    the user's name, class, and college

    Returns a tuple in the form (name, year, college)
    """
    # Rice 411 lookup directory
    url = "http://fouroneone.rice.edu/query.php?tab=people&search=" + net_id + "&department=&phone=&action=Search"
    data = urllib2.urlopen(url)
    name = ""
    year = ""
    college = ""
    # Parsing HTML data like this is highly unpredictable. Thus, a bunch of try-excepts:
    for line in data.readlines()[200:]:
        if "name: " in line:
            try:
                name_list = line.strip().lstrip("name: <b>").rstrip(">b/<").split(", ")
                name = name_list[1] + " " + name_list[0]
            except:
                print("Error getting name")
        if "class: " in line:
            try:
                year = line.strip()[7:].split()[0]
            except:
                print("Error getting year")
        if "college: " in line:
            try:
                college = line.strip()[9:]
            except:
                print("Error getting college")
    return (name, year, college)


def allowed_file(filename):
    """
    Check if the file is of a permissible file extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def file_extension(filename):
    """
    Get the file extension of file. Excludes the "." before the extension.
    """
    return filename.rsplit('.', 1)[1]


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
