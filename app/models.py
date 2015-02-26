from app import db


class Profile(db.Model):
    """
    Database model representing a user profile. See below for detailed descriptions of each column.
    """
    # Columns for user profile table
    net_id = db.Column(db.String(64), primary_key=True, unique=True, index=True)
    name = db.Column(db.String(255))
    year = db.Column(db.String(255))
    dob = db.Column(db.Integer)
    college = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    bio = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    account_type = db.Column(db.String(255))
    listings = db.relationship('Listing', backref='author', lazy='dynamic')
    listing_photos = db.relationship('Photo', backref='author', lazy='dynamic')
    preferences = db.relationship('Preferences', backref='author', lazy='dynamic')

    def __init__(self, net_id, account_type, name, year, dob, college, gender, bio, facebook=None, photo=None):
        self.net_id = net_id  # User's Net ID
        self.account_type = account_type  # Either "filler" or "joiner"
        self.name = name  # Name
        self.year = year  # Class level (freshman, sophomore, ...)
        self.dob = dob  # String representation of birthday (MM/DD/YYYY)
        self.college = college  # Residential college
        self.gender = gender  # Male, female, or other
        self.bio = bio  # String, user-inputted bio
        self.facebook = facebook  # Facebook ID (if the user connected with Facebook)
        self.photo = photo  # String representation of the hash of the uploaded photo (if the user uploaded a photo)

    def __repr__(self):
        return '<User %r>' % self.net_id

    def to_json(self):
        return {
            "net_id" : self.net_id,
            "name" : self.name,
            "year" : self.year,
            "dob" :  self.dob,
            "college" : self.college,
            "gender" : self.gender,
            "bio" : self.bio,
            "facebook" : self.facebook,
            "photo" : self.photo,
            "account_type" : self.account_type
        }


class Listing(db.Model):
    """
    Database model representing a listing. See below for detailed descriptions of each column.
    """
    # Columns for listings table
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    poster_netid = db.Column(db.String(64), db.ForeignKey('profile.net_id'))
    apartment_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    address_line_1 = db.Column(db.String(255))
    address_line_2 = db.Column(db.String(255))
    distance = db.Column(db.Float)
    rent = db.Column(db.Float)
    rent_details = db.Column(db.String(255))
    property_size = db.Column(db.Integer)
    number_roommates_needed = db.Column(db.Integer)
    timestamp = db.Column(db.String(255))
    review_url = db.Column(db.String(255))
    review_rating = db.Column(db.String(255))
    review_snippet = db.Column(db.String(255))
    amenities_gym = db.Column(db.String(64))
    amenities_pool = db.Column(db.String(64))
    amenities_pet_friendly = db.Column(db.String(64))
    amenities_computer_room = db.Column(db.String(64))
    amenities_trash_pickup_services = db.Column(db.String(64))
    photos = db.relationship('Photo', backref='listing', lazy='dynamic')

    def __init__(self, poster_netid, apartment_name, description, address_line_1, address_line_2, distance, rent,
                 rent_details, property_size, number_roommates_needed, timestamp, review_url, review_rating,
                 review_snippet, has_gym, has_pool, is_pet_friendly, has_computer_room, has_trash_pickup_services):
        self.poster_netid = poster_netid  # Net ID of the listing poster
        self.apartment_name = apartment_name  # Name of the apartment
        self.description = description  # Description of the listing
        self.address_line_1 = address_line_1  # Address lines
        self.address_line_2 = address_line_2
        self.distance = distance  # Distance of apartment from Rice
        self.rent = rent  # Monthly rent
        self.rent_details = rent_details  # Elaboration on monthly rent
        self.property_size = property_size  # Size of property, in sq ft
        self.number_roommates_needed = number_roommates_needed  # Number of roommates the filler needs
        self.timestamp = timestamp  # When the listing was posted
        self.review_url = review_url  # URL of the Yelp listing
        self.review_rating = review_rating  # URL of the Yelp rating image
        self.review_snippet = review_snippet  # Snippet of the most recent Yelp review
        # Filter conditions
        self.amenities_gym = has_gym
        self.amenities_pool = has_pool
        self.amenities_pet_friendly = is_pet_friendly
        self.amenities_computer_room = has_computer_room
        self.amenities_trash_pickup_services = has_trash_pickup_services

    def __repr__(self):
        return '<Listing %r>' % self.id

    def to_json(self):
        return {
            "id" : self.id,
            "poster_netid" : self.poster_netid,
            "apartment_name" : self.apartment_name,
            "description" : self.description,
            "address_line_1" : self.address_line_1,
            "address_line_2" : self.address_line_2,
            "distance" : self.distance,
            "rent" : self.rent,
            "rent_details" : self.rent_details,
            "property_size" : self.property_size,
            "number_roommates_needed" : self.number_roommates_needed,
            "timestamp" : self.timestamp,
            "review_url" : self.review_url,
            "review_rating" : self.review_rating,
            "review_snippet" : self.review_snippet,
            "amenities_gym" : self.amenities_gym,
            "amenities_pool" : self.amenities_pool,
            "amenities_pet_friendly" : self.amenities_pet_friendly,
            "amenities_computer_room" : self.amenities_computer_room,
            "amenities_trash_pickup_services" : self.amenities_trash_pickup_services
        }


class Preferences(db.Model):
    """
    Database model storing user apartment preferences that are selected on account creation.
    """
    # Columns for preferences table
    net_id = db.Column(db.String(64), db.ForeignKey('profile.net_id'), primary_key=True, unique=True, index=True)
    # Default sorting preference
    sorting_preference = db.Column(db.String(64))
    # Amenities pre-checked preferences
    amenities_gym = db.Column(db.String(64))
    amenities_pool = db.Column(db.String(64))
    amenities_pet_friendly = db.Column(db.String(64))
    amenities_computer_room = db.Column(db.String(64))
    amenities_trash_pickup_services = db.Column(db.String(64))

    def __init__(self, net_id, sorting_preference, has_gym, has_pool, is_pet_friendly, has_computer_room, has_trash_pickup_services):
        self.net_id = net_id
        self.sorting_preference = sorting_preference  # One of "distance", "rent", "size"
        self.amenities_gym = has_gym
        self.amenities_pool = has_pool
        self.amenities_pet_friendly = is_pet_friendly
        self.amenities_computer_room = has_computer_room
        self.amenities_trash_pickup_services = has_trash_pickup_services

    def __repr__(self):
        return '<Preferences %r>' % self.net_id

    def to_json(self):
        return {
            "net_id" : self.net_id,
            "sorting_preference" : self.sorting_preference,
            "amenities_gym" : self.amenities_gym,
            "amenities_pool" : self.amenities_pool,
            "amenities_pet_friendly" : self.amenities_pet_friendly,
            "amenities_computer_room" : self.amenities_computer_room,
            "amenities_trash_pickup_services" : self.amenities_trash_pickup_services
        }


class Photo(db.Model):
    """
    Database model representing a photo added to a listing. See below for detailed descriptions of each column.
    """
    # Columns for listings table
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    hash = db.Column(db.String(255))
    net_id = db.Column(db.String(64), db.ForeignKey('profile.net_id'))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'))

    def __init__(self, photo, net_id, listing_id):
        self.hash = photo # String representation of the hash of the uploaded photo
        self.net_id = net_id
        self.listing_id = listing_id

    def __repr__(self):
        return '<Photo %r>' % self.id

    def to_json(self):
        return {
            "hash" : self.hash,
            "net_id" : self.net_id,
            "listing_id" : self.listing_id
        }