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
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, net_id, name, year, dob, college, gender, bio, facebook=None, photo=None):
        self.net_id = net_id  # User's Net ID
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


class Post(db.Model):
    # Columns for user post table
    id = db.Column(db.Integer, primary_key = True, unique = True)
    apartment_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    rent = db.Column(db.Integer)
    body = db.Column(db.String(255)) # temporary
    timestamp = db.Column(db.DateTime)
    net_id = db.Column(db.String(64),  db.ForeignKey('profile.net_id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)