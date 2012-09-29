from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.BigInteger)
    event_id = db.Column(db.BigInteger)
    available = db.Column(db.String)
    votes = db.relationship('Vote')

    def __init__(self, author_id, event_id, available):
        self.author_id = author_id
        self.event_id = event_id
        self.available = available


class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger)
    user_name = db.Column(db.String(80))
    event = db.Column(db.Integer, db.ForeignKey('event.id'))
    vote = db.Column(db.String)

    def __init__(self, user_id, user_name, event, vote):
        self.user_id = user_id
        self.user_name = user_name
        self.event = event
        self.vote = vote
