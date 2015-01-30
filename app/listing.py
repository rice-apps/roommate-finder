import os
import datetime

from flask import render_template, session, request
import requests
from werkzeug.utils import secure_filename, redirect

from app import app, db, email
from app.models import Profile, Preferences, Listing, Photo
from app.profile import file_extension, allowed_file


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff'])

@app.route('/new_listing', methods=['POST'])
def new_listing():
    """
    Processes form data in POST request from listing creation page and adds the listing to the database table Listing.

    The profile photo associated with the user is recorded in the column "photo" in the Profile table.
    It is stored as <hash>.<file_extension> where <hash> is a hash is a hash of the uploaded photo and <file_extension> is...well, the file extension.
    The actual photo file is stored as app/photos/<hash>.<file_extension>
    """

    # Fields from listing form
    fields = ["apartment_name", "description", "address_line_1", "address_line_2", "distance", "rent", "rent_details",
              "property_size", "number_roommates_needed", "amenities_gym", "amenities_pool", "amenities_pet_friendly",
              "amenities_computer_room", "amenities_trash_pickup_services"]

    # Get user-entered values from form
    values = {}
    print "here"
    i = 1
    for field in fields:
        print(i)
        print(field)
        i+=1
        values[field] = request.form[field]
        print(values[field])


    # Uploaded apartment pictures
    photos = request.files.getlist('photos[]')
    print ("photos")
    print photos
    print type(photos)

    # The user selected a photo of an invalid file extension
    # Redirect the user to an error page
    for photo in photos:
        if photo and not allowed_file(photo.filename):
            data = {"net_id": values["net_id"], "name": values["name"], "year": values["year"], "dob": values["dob"], "college": values["college"], "gender": values["gender"], "bio": values["bio"], "facebook": values["facebook"], "error": "Error: invalid photo file extension ." + str(file_extension(photo.filename))}
            return render_template('profile_creation.html', data=data)

    photo_hashes = []
    # Store the user's profile photos on the server
    for photo in photos:
        if photo and allowed_file(photo.filename):
            # Create hash of the uploaded picture
            photo_hashes.append(str(hash(photo)))
            filename = secure_filename(photo_hashes[-1]) + "." + file_extension(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_hashes[-1] += "." + file_extension(photo.filename)

    print photo_hashes

    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
    print("netid = " + net_id)


    # Convert unicodes corresponding to numbers into floats or integers
    values["distance"] = float(str(values["distance"]))
    values["rent"] = float(str(values["rent"]))
    values["property_size"] = int(str(values["property_size"]))
    values["number_roommates_needed"] = int(str(values["number_roommates_needed"]))

    # Process amenities checkboxes to be consistent with db format - 'true'/'false' (string)
    values["amenities_gym"] = "true" if str(values["amenities_gym"]) == "on" else "false"
    values["amenities_pool"] = "true" if str(values["amenities_pool"]) == "on" else "false"
    values["amenities_pet_friendly"] = "true" if str(values["amenities_pet_friendly"]) == "on" else "false"
    values["amenities_computer_room"] = "true" if str(values["amenities_computer_room"]) == "on" else "false"
    values["amenities_trash_pickup_services"] = "true" if str(values["amenities_trash_pickup_services"]) == "on" else "false"

    # Create a new listing from the Listing model
    listing = Listing(values["apartment_name"], values["description"], values["address_line_1"], values["address_line_2"],
                      values["distance"], values["rent"], values["rent_details"], values["property_size"],
                      values["number_roommates_needed"], str(datetime.datetime.utcnow()), values["amenities_gym"], values["amenities_pool"],
                      values["amenities_pet_friendly"], values["amenities_computer_room"], values["amenities_trash_pickup_services"], net_id)

    # Add this new listing to the database
    db.session.add(listing)
    db.session.commit()

    print("listing id")
    print listing.id
    # Create new photo db columns based on Photo model and save them in the database
    new_photos = [Photo(photo_hash, net_id, listing.id) for photo_hash in photo_hashes]
    db.session.add_all(new_photos)
    db.session.commit()



    return redirect('/get_started')


@app.route('/delete_listing', methods=['GET', 'POST'])
def delete_listing():
    """
    Removes the user from the database.
    """
    # Get Net ID from GET data
    listing_id = request.args.get('listing_id', '')
    listing_id = int(str(listing_id))

    listing = Listing.query.filter_by(id=listing_id).first()
    print listing
    db.session.delete(listing)
    db.session.commit()
    # Logout the session after profile deletion.
    return redirect('/my_postings')