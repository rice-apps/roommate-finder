from app import db

class Profile(db.Model):
        # Columns for user profile table
        net_id = db.Column(db.String(64), primary_key = True, unique = True, index = True)
        name = db.Column(db.String(255))
        year = db.Column(db.String(255))
        dob = db.Column(db.Integer)
        college = db.Column(db.String(255))
        gender = db.Column(db.String(255))
        bio = db.Column(db.String(255))
        photo = db.Column(db.String(255))

        def __init__(self, net_id, name, year, dob, college, gender, bio, photo=None):
            self.net_id = net_id
            self.name = name
            self.year = year
            self.dob = dob
            self.college = college
            self.gender = gender
            self.bio = bio
            self.photo = photo

        def __repr__(self):
                return '<User %r>' % self.net_id
