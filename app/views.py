# views.py
# This file contains all methods related to routing, and directing the user to the correct location.
import json

import urllib2
import time

from flask import render_template, session, send_from_directory, request, jsonify
from werkzeug.utils import redirect

from app import app, lm, db, email
from app.models import Profile, Listing, Preferences, Photo


# Server upload folder - do not change
UPLOAD_FOLDER = "Z:/RoommateFinder/roommate-finder/app/photos"
# Local dev environment upload folder - change as necessary
# UPLOAD_FOLDER = "D:/GitHub/roommate-finder/app/photos"

app.config['CAS_SERVER'] = 'https://netid.rice.edu'
app.config['CAS_AFTER_LOGIN'] = 'after_login'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APP_FOLDER'] = "Z:/RoommateFinder/roommate-finder"  # directory of application on the server - do not change
# app.config['APP_FOLDER'] = "D:/GitHub/roommate-finder"  # local directory
app.config['APP_URL'] = 'http://roommatefinder.riceapps.org'
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


@app.route('/', methods=['GET'])
def index():
    """
    First check if the user is logged in. If so, and he/she has an account, redirect him/her to the main search page.
    If not, redirect him/her to the intro page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()
    if net_id is not None and user is not None:
        data = {"net_id": net_id, "profile": user}
        return render_template('action.html', data=data)
    else:
        return app.send_static_file('intro.html')


@app.route('/about')
def about():
    """
    About page. Code below checks if user is logged in and exists in DB.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()
    if net_id and user:
        # Appropriately package the user's data if the user is logged in and has a profile set up
        data = {"net_id": net_id, "profile": user}
        return render_template('about.html', data=data)
    else:
        # Return the same page, but with null data
        return render_template('about.html', data={"net_id": None, "profile": None})


@app.route('/photos/<path:filename>')
def photos(filename):
    """
    Proper routing of /photos, the uploaded profile pictures directory.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route('/directions_api', methods=['POST'])
def directions_api():
    """
    Returns the distance to a destination from Rice, via the Google Maps Directions API.
    The API is not called directly in Javascript because of cross-origin request security issues.
    """
    destination = request.args.get("destination", None)
    if destination:
        try:
            destination = destination.replace(" ", "+")
            directions_data = urllib2.urlopen("https://maps.googleapis.com/maps/api/directions/json?origin=6100+Main+St+Houston+TX+77005&destination=" + destination + "&key=AIzaSyChrd2_zI_bHbhUnyw1P7-e8wf2Rq9uiiQ").read()
            directions_data_json = json.loads(directions_data)
            return directions_data_json["routes"][0]["legs"][0]["distance"]["text"].split(" ")[0]  # dear god
        except:
            return "Error"
    else:
        return "Error"


@app.route('/app.db')
def database():
    """
    URL to get the SQLite database. Required for JS-SQL behavior in search.js.
    """
    return send_from_directory(app.config["APP_FOLDER"], "app.db")


@app.route('/welcome')
def welcome():
    """
    First ensure that there is a valid CAS login. Then, present the user with a page allowing him/her to select
    filler or joiner status.
    """
    # User Net ID
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)

    # Check if there is even someone logged in
    if login is None:
        return redirect("/login")

    # Check if the user exists in the database. If so, the user shouldn't even be here
    user = Profile.query.filter_by(net_id=login).first()
    if user is not None:
        return redirect("/my_profile")

    # Get user details from Rice public directory
    (name, year, college) = get_user_details(login)
    data = {"net_id": login, "name": name, "first_name": name.split(" ")[0], "year": year, "college": college}
    return render_template("account_type_selection.html", data=data)


@app.route('/after_login', methods=['GET'])
def after_login():
    """
    If the user doesn't yet exist in the database, show the welcome screen. Otherwise, show the My Account interface.
    """
    # User Net ID
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)

    # Try to find Net ID in database
    user = Profile.query.filter_by(net_id=login).first()
    if user is None:
        # User doesn't exist in DB
        # Redirect the user to the main welcome page
        return redirect("/welcome")
    else:
        # User does exist in DB
        # Redirect user to main page
        return redirect('/')


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
    return name, year, college


@app.route('/get_started')
def get_started():
    """
    Welcome to Roommate Finder; here's how to get started.
    """
    # User Net ID
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()

    if user is None:
        # The user might have been taken here from the welcome page, if he/she chose to be a joiner. In this case,
        # create a profile for the user with only the name field filled out, so that he/she has a profile in the
        # database. Fillers are required to go through the entire process of filling out a profile.
        (name, year, college) = get_user_details(net_id)
        user = Profile(net_id, "joiner", name, year.capitalize(), None, college, None, None)
        prefs = Preferences(net_id, None, "false", "false", "false", "false", "false")
        db.session.add(user)
        db.session.add(prefs)
        db.session.commit()
        # Send a lovely welcome email
        email.welcome_email(net_id)

    # Do this again since a user might have been just added
    user = Profile.query.filter_by(net_id=net_id).first()

    if net_id is not None and user is not None:
        data = {"net_id": net_id, "profile": user}
        return render_template('welcome.html', data=data)


@app.route('/create_listing')
def create_listing():
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()
    if net_id and user:
        if user.account_type == "joiner":
            return render_template("create_new_listing_error.html", data={"profile": user})
        data = {"net_id": net_id, "profile": user}
        return render_template("listing_creation.html", data = data)
    else:
        return redirect('/login')


@app.route('/action')
def action():
    """
    Action page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user}
        return render_template('action.html', data=data)
    else:
        return redirect('/login')


@app.route('/users')
def users():
    """
    Browse users page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user}
        return render_template('users_list.html', data=data)
    else:
        return redirect('/login')

@app.route('/get_users', methods=['GET'])
def get_users():
    """
    Returns all the users data in JSON format. It gets called by frontend users.js.
    """
    users = Profile.query.all()
    users_list = map(Profile.to_json, users)
    result = { "users": users_list }
    return jsonify(result)


@app.route('/search')
def search():
    """
    Main search interface.
    """
    # User Net ID
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()

    if net_id and user:
        user = Profile.query.filter_by(net_id=net_id).first()
        preferences = Preferences.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user, "preferences": preferences}
        return render_template('search.html', data=data)
    else:
        return redirect('/login')

@app.route('/get_search_data')
def get_search_data():
    """
    Returns all the data required for search: listings, search preferences, and photos.
    The data is in JSON format. It gets called by frontend search.js.
    """
    result = {}

    listings = db.session.query(Listing).join(Profile).filter(Listing.poster_netid==Profile.net_id).all()
    listings_list = map(Listing.to_json, listings)
    result["listings"] = listings_list
    # Add author name to each JSON listing (author name originally from Profile table).
    for num in range(len(listings_list)):
        listings_list[num]["author_name"] = listings[num].author.name

    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    preferences = Preferences.query.filter_by(net_id=net_id).all()
    preferences_list = map(Preferences.to_json, preferences)
    result["preferences"] = preferences_list

    photos = Photo.query.all()
    photos_list = map(Photo.to_json, photos)
    result["photos"] = photos_list

    return jsonify(result)


@app.route('/new_account')
def new_account():
    """
    Renders template for UI for creating a new profile.
    """
    # User Net ID
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is None:
        return redirect('/login')
    # Check if the user exists.
    user = Profile.query.filter_by(net_id=net_id).first()
    if user is None:
        # Get user details from Rice public directory
        (name, year, college) = get_user_details(net_id)
        data = {"net_id": net_id, "name": name, "first_name": name.split(" ")[0], "year": year, "college": college}
        return render_template("profile_creation.html", data=data)
    else:
        return redirect('/my_profile')


@app.route('/my_profile')
def my_profile():
    """
    Edit my profile page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        prefs = Preferences.query.filter_by(net_id=net_id).first()
        data = {"net_id": net_id, "profile": user, "preferences": prefs}
        return render_template('my_profile.html', data=data)
    else:
        return redirect('/login')


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
        return redirect('/')


@app.route('/my_postings')
def my_postings():
    """
    Page showing the user's postings.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
        listings = Listing.query.filter_by(poster_netid=net_id).all()
        print(listings)
        data = {"net_id": net_id, "profile": user, "listings": listings}
        return render_template('my_postings.html', data=data)
    else:
        return redirect('/login')


@app.route('/privacy_policy')
def privacy_policy():
    """
    Privacy policy page.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()
    if net_id and user:
        # Appropriately package the user's data if the user is logged in and has a profile set up
        data = {"net_id": net_id, "profile": user}
        return render_template('privacy_policy.html', data=data)
    else:
        # Return the same page, but with null data
        return render_template('privacy_policy.html', data={"net_id": None, "profile": None})


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
    logged_in_user = Profile.query.filter_by(net_id=login).first()
    data = {"profile": user, "logged_in_profile": logged_in_user, "net_id": path, "net_id_uppercase": path.upper(), "net_id_lowercase": path.lower(), "logged_in_net_id": login}
    # Meh; too many net ID's to keep track of...
    if user:
        data["name_uppercase"] = user.name.upper()
        data["name_lowercase"] = user.name.lower()
        data["name_first_uppercase"] = str(user.name).split()[0].upper()
        data["college_uppercase"] = user.college.upper()
        data["college_lowercase"] = user.college.lower()
        data["year_uppercase"] = user.year.upper()
        data["year_lowercase"] = user.year.lower()
        data["age"] = compute_age(user.dob)
    return render_template('user.html', data=data)


def compute_age(dob):
    """
    Given a MM/DD/YYYY formatted date of birth, calculate current age (relative to now, of course).
    """
    # Try-catch here because the user might be a joiner and thus might not have filled out their DOB.
    try:
        birth_date = dob.split("/")
        age = int(time.strftime("%Y")) - int(birth_date[2])
        if int(time.strftime("%m")) / float(birth_date[0]) < 1:
            age -= 1
        if int(time.strftime("%m")) == int(birth_date[0]) and int(time.strftime("%d")) < int(birth_date[1]):
            age -= 1
        return age
    except:
        return "N/A"


@lm.user_loader
def load_user(id):
    return Profile.query.get(int(id))


# ERROR HANDLERS
@app.errorhandler(500)
def internal_server_error(e):
    return app.send_static_file('error/500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('error/404.html'), 404
