import os
import urllib2

from flask import render_template, session, request, send_from_directory
import time
from werkzeug.utils import secure_filename, redirect

from app import app, db, lm
from app.models import Profile


# This needs to be an absolute path. That's so stupid.
# UPLOAD_FOLDER = "Z:/RoommateFinder/roommate-finder/app/photos"
# Upload folder for local development environment.
UPLOAD_FOLDER = "D:/GitHub/roommate-finder/app/photos"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APP_URL'] = 'http://roommatefinder.kevinlin.info'
app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


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
    fields = ["net_id", "name", "year", "dob", "college", "gender", "bio"]
    # Get user-entered values from form
    values = {}
    for field in fields:
        values[field] = request.form[field]
    # Uploaded profile photo
    photo = request.files['photo']
    # Generate a string representation of a hash of the photo
    # This associates the local copy of the file with the user in the database
    photo_hash = str(hash(photo))
    # Create a new user from the Profile model
    if photo:
        user = Profile(values["net_id"], values["name"], values["year"], values["dob"], values["college"], values["gender"], values["bio"], photo_hash + "." + file_extension(photo.filename))
    else:
        user = Profile(values["net_id"], values["name"], values["year"], values["dob"], values["college"], values["gender"], values["bio"])
    # The user selected a photo of an invalid file extension
    # Redirect the user to an error page
    if photo and not allowed_file(photo.filename):
        data = {"net_id": values["net_id"], "name": values["name"], "year": values["year"], "dob": values["dob"], "college": values["college"], "gender": values["gender"], "bio": values["bio"], "error": "Error: invalid photo file extension ." + str(file_extension(photo.filename))}
        return render_template('profile_creation.html', data=data)
    # Store the user's profile photo on the server
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo_hash) + "." + file_extension(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Add this new user to the database
    db.session.add(user)
    db.session.commit()
    data = {"net_id": values["net_id"], "profile": user}
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
    user.dob = request.form["dob"]
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
    # Logout the session after profile deletion.
    return redirect("/logout", code=302)


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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_extension(filename):
    """
    Get the file extension of file. Excludes the "." before the extension.
    """
    return filename.rsplit('.', 1)[1]


@app.route('/', methods=['GET'])
def index():
    """
    First check if the user is logged in. If so, redirect him/her to the main search page.
    If not, redirect him/her to the intro page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        data = {"net_id": net_id}
        return render_template('search.html', data=data)
    else:
        return app.send_static_file('intro.html')


@app.route('/about')
def about():
    return app.send_static_file('about.html')


@app.route('/delete_account')
def delete_account():
    """
    Delete user account page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        data = {"net_id": net_id}
        return render_template('delete_account.html', data=data)
    else:
        # Redirect user to intro
        index()


@app.route('/my_profile')
def my_profile():
    """
    Edit my profile page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user}
        return render_template('my_profile.html', data=data)
    else:
        index()


@app.route('/my_postings')
def my_postings():
    """
    Page showing the user's postings.

    Yet to be implemented.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user}
        return render_template('my_postings.html', data=data)
    else:
        index()


@app.route('/user/<path:path>')
def user_profile(path):
    """
    Handles routing of /user/net_id (returns that person's profile page)
    """
    # Get the currently logged in user
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if login is None:
        return redirect("/login", code=302)
    # Check if such a net ID even exists
    user = Profile.query.filter_by(net_id=path).first()
    # Stylistic typographic choices: uppercase and lowercase versions
    # I'm sure there's an easier way to do this
    data = {}
    data["profile"] = user
    data["net_id"] = path
    # Meh; too many net ID's to keep track of...
    data["logged_in_net_id"] = login
    if user is not None:
        data["net_id_uppercase"] = path.upper()
        data["net_id_lowercase"] = path.lower()
        data["name_uppercase"] = user.name.upper()
        data["name_lowercase"] = user.name.lower()
        data["name_first_uppercase"] = str(user.name).split()[0].upper()
        data["college_uppercase"] = user.college.upper()
        data["college_lowercase"] = user.college.lower()
        data["year_uppercase"] = user.year.upper()
        data["year_lowercase"] = user.year.lower()
        data["age"] = compute_age(user.dob)
        return render_template('user.html', data=data)
    else:
        # If user doesn't exist, profile key will map to None.
        return render_template('user_not_exists.html', data=data)


def compute_age(dob):
    """
    Given a MM/DD/YYYY formatted date of birth, calculate current age (relative to now, of course).
    """
    birth_date = dob.split("/")
    age = int(time.strftime("%Y")) - int(birth_date[2])
    if int(time.strftime("%m"))/float(birth_date[0]) < 1:
        age -= 1
    if int(time.strftime("%m")) == int(birth_date[0]) and int(time.strftime("%d")) < int(birth_date[1]):
        age -= 1
    return age


@lm.user_loader
def load_user(id):
    return Profile.query.get(int(id))
