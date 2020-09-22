from . import db

class Messages(db.Model):
    """ A Model of messages table """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __repr__(self):
        return f"Message saved: {self.message}" 