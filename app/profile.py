# profile.py
# This file contains all methods related to manipulation of the user profile in the database.
# This includes creating a new user, modifying an existing user, and deleting a user.


import os

from flask import render_template, session, request
import requests
from werkzeug.utils import secure_filename, redirect

from app import app, db, email
from app.models import Profile, Preferences


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])


@app.route('/create_profile', methods=['POST'])
def create_user():
    """
    Processes form data in POST request from profile creation page and adds the user to the database table Profile.

    The profile photo associated with the user is recorded in the column "photo" in the Profile table.
    It is stored as <hash>.<file_extension> where <hash> is a hash is a hash of the uploaded photo and <file_extension> is...well, the file extension.
    The actual photo file is stored as app/photos/<hash>.<file_extension>
    """
    # Fields from form
    fields = ["net_id", "account_type", "name", "year", "dob", "college", "gender", "bio", "facebook", "facebook_photo"]
    # Get user-entered values from form
    values = {}
    for field in fields:
        values[field] = request.form[field]
    photo_hash = None

    # Store search preferences for user
    preference_fields = ["filtering_preference_gym", "filtering_preference_pool", "filtering_preference_pet_friendly", "filtering_preference_computer_room", "filtering_preference_trash_pickup_services"]
    filtering_preferences = [request.form.get(pref, None) is not None for pref in preference_fields]
    prefs = Preferences(values["net_id"], request.form.get("sorting_preference", None), str(filtering_preferences[0]).lower(), str(filtering_preferences[1]).lower(), str(filtering_preferences[2]).lower(), str(filtering_preferences[3]).lower(), str(filtering_preferences[4]).lower())
    db.session.add(prefs)
    db.session.commit()

    # Check for Facebook account connection: if the user connected an account, then the ID is a string of
    # numbers without spaces; otherwise, it's just the placeholder text, which should be None
    # If the user connected an account, store the profile photo
    if values["facebook"].count(" ") > 0:
        values["facebook"] = None
    else:
        try:
            facebook_photo = requests.get(values["facebook_photo"])
            # Generate a string representation of a hash of the photo
            # This associates the local copy of the file with the user in the database
            photo_hash = str(hash(facebook_photo))
            # Save the file locally to /app/photos
            with open(app.config["UPLOAD_FOLDER"] + "/" + photo_hash + "." + file_extension(values["facebook_photo"][:values["facebook_photo"].rfind("?")]), "wb") as f:
                f.write(facebook_photo.content)
        except:
            pass

    # Uploaded profile photo (if exists)
    photo = request.files['photo']

    # Create a new user from the Profile model
    if photo:
        photo_hash = str(hash(photo))
        user = Profile(values["net_id"], values["account_type"].lower(), values["name"], values["year"], values["dob"], values["college"], values["gender"], values["bio"], values["facebook"], photo_hash + "." + file_extension(photo.filename))
    elif not photo and photo_hash:
        user = Profile(values["net_id"], values["account_type"].lower(), values["name"], values["year"], values["dob"], values["college"], values["gender"], values["bio"], values["facebook"], photo_hash + "." + file_extension(values["facebook_photo"][:values["facebook_photo"].rfind("?")]))
    else:
        user = Profile(values["net_id"], values["account_type"].lower(), values["name"], values["year"], values["dob"], values["college"], values["gender"], values["bio"], values["facebook"])

    # The user selected a photo of an invalid file extension
    # Redirect the user to an error page
    if photo and not allowed_file(photo.filename):
        data = {"net_id": values["net_id"], "name": values["name"], "year": values["year"], "dob": values["dob"], "college": values["college"], "gender": values["gender"], "bio": values["bio"], "facebook": values["facebook"], "error": "Error: invalid photo file extension ." + str(file_extension(photo.filename))}
        return render_template('profile_creation.html', data=data)

    # Store the user's profile photo on the server
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo_hash) + "." + file_extension(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Add this new user to the database
    db.session.add(user)
    db.session.commit()

    # Send him or her a welcome email
    try:
        email.welcome_email(values["net_id"])
    except:
        print("Failed to send email. This error is expected if you are in a local development environment.")

    return redirect('/get_started')


@app.route('/update_profile', methods=['POST'])
def update_user():
    """
    Called when the user is modifying is/her account from the My Profile page.
    Updates the database to reflect the user's changes.
    """
    # Retrieve the user by net ID from the database
    user = Profile.query.filter_by(net_id=request.form["net_id"]).first()

    # Update all the profile columns
    user.name = request.form["name"]
    user.account_type = request.form["account_type"].lower()
    user.year = request.form["year"]
    user.dob = request.form["dob"]
    user.college = request.form["college"]
    user.gender = request.form["gender"]
    user.bio = request.form["bio"]
    user.facebook = request.form["facebook"]

    # Update all the preferences columns
    prefs = Preferences.query.filter_by(net_id=request.form["net_id"]).first()
    prefs.sorting_preference = request.form.get("sorting_preference", None)
    prefs.amenities_gym = str(request.form.get("filtering_preference_gym", None) is not None).lower()
    prefs.amenities_pool = str(request.form.get("filtering_preference_pool", None) is not None).lower()
    prefs.amenities_pet_friendly = str(request.form.get("filtering_preference_pet_friendly", None) is not None).lower()
    prefs.amenities_computer_room = str(request.form.get("filtering_preference_computer_room", None) is not None).lower()
    prefs.amenities_trash_pickup_services = str(request.form.get("filtering_preference_trash_pickup_services", None) is not None).lower()


    try:
        facebook_photo = requests.get(request.form["facebook_photo"])
    except:
        facebook_photo = None

    photo = request.files['photo']

    if request.form["facebook"].count(" ") > 0:
        user.facebook = None
    elif facebook_photo and not photo:
        photo_hash = str(hash(facebook_photo))
        user.photo = photo_hash + "." + file_extension(request.form["facebook_photo"][:request.form["facebook_photo"].rfind("?")])
        with open(app.config["UPLOAD_FOLDER"] + "/" + photo_hash + "." + file_extension(request.form["facebook_photo"][:request.form["facebook_photo"].rfind("?")]), "wb") as f:
            f.write(facebook_photo.content)

    if photo and allowed_file(photo.filename):
        photo_hash = str(hash(request.files['photo']))
        filename = secure_filename(photo_hash) + "." + file_extension(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.photo = photo_hash + "." + file_extension(photo.filename)

    if photo and not allowed_file(photo.filename):
        data = {"net_id": request.form["net_id"], "profile": user, "error": "Error: invalid photo file extension ." + str(file_extension(photo.filename))}
        return render_template('my_profile.html', data=data)

    # Commit the changes
    db.session.merge(user)
    db.session.merge(prefs)
    db.session.commit()

    return redirect('/my_profile')


@app.route('/delete_profile', methods=['GET', 'POST'])
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
        prefs = Preferences.query.filter_by(net_id=net_id).first()
        db.session.delete(user)
        db.session.delete(prefs)
        db.session.commit()
    # Logout the session after profile deletion.
    return redirect("/logout", code=302)


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