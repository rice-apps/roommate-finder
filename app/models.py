from app import db

class Profiles(db.Model):
        # Columns for user profile table
        net_id = db.Column(db.String(64), primary_key = True, unique = True, index = True)
        name = db.Column(db.String(255))
        year = db.Column(db.Integer)
        age = db.Column(db.Integer)
        college = db.Column(db.String(255))
        gender = db.Column(db.String(255))
        bio = db.Column(db.String(255))

        def __repr__(self):
                return '<User %r>' % (self.net_id)
