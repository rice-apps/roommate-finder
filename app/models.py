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


class Listing(db.Model):
    """
    Database model representing a listing. See below for detailed descriptions of each column.
    """
    # Columns for listings table
    id = db.Column(db.Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    apartment_name = db.Column(db.String(255))
    poster_netid = db.Column(db.String(255))
    poster_name = db.Column(db.Integer)
    description = db.Column(db.String(255))
    address_line_1 = db.Column(db.String(255))
    address_line_2 = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    distance = db.Column(db.Float)
    rent = db.Column(db.Float)
    rent_details = db.Column(db.String(255))
    property_size = db.Column(db.Integer)
    number_roommates_needed = db.Column(db.Integer)
    timestamp = db.Column(db.String(255))
    amenities_gym = db.Column(db.String(255))
    amenities_pool = db.Column(db.String(64))
    amenities_pet_friendly = db.Column(db.String(64))
    amenities_computer_room = db.Column(db.String(64))
    amenities_trash_pickup_services = db.Column(db.String(64))

    def __init__(self, id, apartment_name, poster_netid, poster_name, description, address_line_1, address_line_2, photo, distance, rent, rent_details, property_size, number_roommates_needed, timestamp, has_gym, has_pool, is_pet_friendly, has_computer_room, has_trash_pickup_services):
        self.id = id  # ID of the listing (used for /listing/ID)
        self.apartment_name = apartment_name  # Name of the apartment
        self.poster_netid = poster_netid  # Net ID of the listing poster
        self.poster_name = poster_name  # Name of the poster
        self.description = description  # Description of the listing
        self.address_line_1 = address_line_1  # Address lines
        self.address_line_2 = address_line_2
        self.photo = photo  # Name of the photo, stored in /photos/listings
        self.distance = distance
        self.rent = rent
        self.rent_details = rent_details
        self.property_size = property_size
        self.number_roommates_needed = number_roommates_needed
        self.timestamp = timestamp
        self.amenities_gym = has_gym
        self.amenities_pool = has_pool
        self.amenities_pet_friendly = is_pet_friendly
        self.amenities_computer_room = has_computer_room
        self.amenities_trash_pickup_services = has_trash_pickup_services

    def __repr__(self):
        return '<Listing %r>' % self.net_id