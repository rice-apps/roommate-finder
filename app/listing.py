# profile.py
# This file contains all methods related to manipulation of listings.



import os

from flask import render_template, session, request
from werkzeug.utils import secure_filename, redirect

from app import app, db, reviews, universal
from app.models import Profile, Listing, Photo
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
    # Get logged in user information
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=net_id).first()

    # Fields from listing form
    fields = ["apartment_name", "description", "address_line_1", "address_line_2", "distance", "rent", "rent_details",
              "property_size", "number_roommates_needed", "amenities_gym", "amenities_pool", "amenities_pet_friendly",
              "amenities_computer_room", "amenities_trash_pickup_services"]

    # Get user-entered values from form
    values = {}
    i = 1
    for field in fields:
        i += 1
        values[field] = request.form[field]
    # Uploaded apartment pictures
    photos = request.files.getlist('photos[]')

    # The user selected a photo of an invalid file extension
    # Redirect the user to an error page
    for photo in photos:
        if photo and not allowed_file(photo.filename):
            data = {"net_id": values["net_id"], "name": values["name"], "year": values["year"], "dob": values["dob"],
                    "college": values["college"], "gender": values["gender"], "bio": values["bio"],
                    "facebook": values["facebook"],
                    "error": "Error: invalid photo file extension ." + str(file_extension(photo.filename))}
            # TODO: Make this more elegant
            return "Sorry, the file extension " + str(file_extension(photo.filename)) + " is not permitted"

    photo_hashes = []
    # Store the user's profile photos on the server
    for photo in photos:
        if photo and allowed_file(photo.filename):
            # Create hash of the uploaded picture
            photo_hashes.append(str(hash(photo)))
            filename = secure_filename(photo_hashes[-1]) + "." + file_extension(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/listings", filename))
            photo_hashes[-1] += "." + file_extension(photo.filename)

    print photo_hashes

    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    if net_id is not None:
        user = Profile.query.filter_by(net_id=net_id).first()
    print("netid = " + net_id)

    # Convert unicodes corresponding to numbers into floats or integers
    values["distance"] = 10#float(str(values["distance"].replace(",", "").split(" ")[0]))
    values["rent"] = float(str(values["rent"]))
    values["property_size"] = int(str(values["property_size"]))
    values["number_roommates_needed"] = int(str(values["number_roommates_needed"]))

    # Process amenities checkboxes to be consistent with db format - 'true'/'false' (string)
    values["amenities_gym"] = "true" if str(values["amenities_gym"]) == "on" else "false"
    values["amenities_pool"] = "true" if str(values["amenities_pool"]) == "on" else "false"
    values["amenities_pet_friendly"] = "true" if str(values["amenities_pet_friendly"]) == "on" else "false"
    values["amenities_computer_room"] = "true" if str(values["amenities_computer_room"]) == "on" else "false"
    values["amenities_trash_pickup_services"] = "true" if str(values["amenities_trash_pickup_services"]) == "on" else "false"

    # Get Yelp review information
    (review_url, review_rating, review_snippet) = get_yelp_reviews(
        values["address_line_1"] + ", " + values["address_line_2"])
    review_snippet = review_snippet.replace('\n', ' ').replace('\r', '')

    # Create a new listing from the Listing model
    listing = Listing(net_id, values["apartment_name"], values["description"], values["address_line_1"],
                      values["address_line_2"],
                      values["distance"], values["rent"], values["rent_details"], values["property_size"],
                      values["number_roommates_needed"], universal.timestamp().split(" ")[0], review_url, review_rating,
                      review_snippet,
                      values["amenities_gym"], values["amenities_pool"], values["amenities_pet_friendly"],
                      values["amenities_computer_room"], values["amenities_trash_pickup_services"])
    # Add this new listing to the database
    db.session.add(listing)
    db.session.commit()

    print("listing id")
    print listing.id
    # Create new photo db columns based on Photo model and save them in the database
    new_photos = [Photo(photo_hash, net_id, listing.id) for photo_hash in photo_hashes]
    db.session.add_all(new_photos)
    db.session.commit()

    return redirect('/listing/' + str(listing.id))


@app.route('/delete_listing', methods=['GET', 'POST'])
def delete_listing():
    """
    Removes the listing from the database.
    """
    # Get Net ID from GET data
    listing_id = request.args.get('listing_id', '')
    listing_id = int(str(listing_id))

    listing = Listing.query.filter_by(id=listing_id).first()
    db.session.delete(listing)
    db.session.commit()
    # Logout the session after profile deletion.
    return redirect('/my_postings')


@app.route('/update_listing', methods=['POST'])
def update_listing():
    """
    Updates the listing.
    """
    # Logged in user
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)

    # Retrieve the listing from the database
    listing = Listing.query.filter_by(id=request.form["listing_id"]).first()

    values = {}
    # Process amenities checkboxes to be consistent with db format - 'true'/'false' (string)
    values["amenities_gym"] = "true" if str(request.form["amenities_gym"]) == "on" else "false"
    values["amenities_pool"] = "true" if str(request.form["amenities_pool"]) == "on" else "false"
    values["amenities_pet_friendly"] = "true" if str(request.form["amenities_pet_friendly"]) == "on" else "false"
    values["amenities_computer_room"] = "true" if str(request.form["amenities_computer_room"]) == "on" else "false"
    values["amenities_trash_pickup_services"] = "true" if str(request.form["amenities_trash_pickup_services"]) == "on" else "false"

    # Update all the profile columns
    listing.apartment_name = request.form["apartment_name"]
    listing.description = request.form["description"]
    listing.address_line_1 = request.form["address_line_1"]
    listing.address_line_2 = request.form["address_line_2"]
    listing.distance = float(str(request.form["distance"].replace(",", "").split(" ")[0]))
    listing.rent = float(str(request.form["rent"]))
    listing.rent_details = request.form["rent_details"]
    listing.property_size = int(str(request.form["property_size"]))
    listing.number_roommates_needed = int(str(request.form["number_roommates_needed"]))
    listing.amenities_gym = values["amenities_gym"]
    listing.amenities_pool = values["amenities_pool"]
    listing.amenities_pet_friendly = values["amenities_pet_friendly"]
    listing.amenities_computer_room = values["amenities_computer_room"]
    listing.amenities_trash_pickup_services = values["amenities_trash_pickup_services"]

    photo_hashes = []
    # Store the user's profile photos on the server
    for photo in request.files.getlist('photos[]'):
        if photo and allowed_file(photo.filename):
            # Create hash of the uploaded picture
            photo_hashes.append(str(hash(photo)))
            filename = secure_filename(photo_hashes[-1]) + "." + file_extension(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/listings", filename))
            photo_hashes[-1] += "." + file_extension(photo.filename)

    new_photos = [Photo(photo_hash, net_id, listing.id) for photo_hash in photo_hashes]
    db.session.add_all(new_photos)
    db.session.commit()

    db.session.merge(listing)
    db.session.commit()

    return redirect('/listing/' + str(listing.id))


@app.route('/edit_listing/<path:ID>')
def edit_listing(ID):
    """
    Edit the listing identified by the ID
    """
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=login).first()
    if user:
        listing = Listing.query.filter_by(id=ID).first()
        data = {"profile": user, "net_id": login, "error": None, "listing": listing}
        if listing:
            return render_template("update_listing.html", data=data)
        else:
            return render_template("update_listing_error.html", data=data)
    else:
        return redirect('/login')


@app.route('/listing/<path:ID>')
def listing_details(ID):
    """
    Handles routing of /listing/ID (returns that listing's full detail page)
    """
    # Initialize a null error and listing poster
    error = None
    poster = None
    # Get the currently logged in user
    login = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = Profile.query.filter_by(net_id=login).first()
    if login is None:
        return redirect("/login", code=302)
    # Get the requested listing from the database
    photo_hashes = None
    listing = Listing.query.filter_by(id=ID).first()
    if not listing:
        error = "This listing doesn't exist!"
    else:
        poster = Profile.query.filter_by(net_id=listing.poster_netid).first()
        photos = listing.photos.filter_by(listing_id=listing.id).all()
        if len(photos) > 0:
            photo_hashes = [photo.hash for photo in listing.photos.filter_by(listing_id=listing.id).all()]
    data = {"net_id": login, "profile": user, "id": ID, "listing": listing, "error": error, "poster": poster,
            "address": listing.address_line_1 + ", " + listing.address_line_2, "photos": photo_hashes}
    return render_template('listing_detail.html', data=data)


def get_yelp_reviews(address):
    """
    Gets the Yelp rating and review for the business located at the passed address.
    Returns a 3-length tuple of (business url, rating image url, review snippet)

    Example input: "6100 Main St, Houston, TX, 77005"
    Example output: ("http://www.yelp.com/biz/rice-university", "http://yelp.com/image/for/5/star.png", "Fantastic school!")
    """
    url = str(reviews.search("", address)["businesses"][0]["url"])
    rating = str(reviews.search("", address)["businesses"][0]["rating_img_url"])
    review_snippet = str(reviews.search("", address)["businesses"][0]["snippet_text"])
    return (url, rating, review_snippet)
