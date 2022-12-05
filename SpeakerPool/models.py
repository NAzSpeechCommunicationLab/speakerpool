from SpeakerPool import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(50), nullable=False)
    researcher = db.Column(db.Boolean, default=False, nullable=False)
    studies = db.relationship('StudyEntry', backref='researcher', lazy=True)

    def __repr__(self):
        return f"""\tParticipant Number: {self.id}
        Username: {self.username}
        Email: {self.email}
        Researcher: {self.researcher}
        Studies Created:\n {self.studies}\n"""

class StudyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_name = db.Column(db.String(300), unique=True, nullable=False)
    date_started = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    participant_description = db.Column(db.String(800), nullable=False)
    text_type = db.Column(db.String(300), nullable=False)
    n_participants = db.Column(db.Integer, nullable=False, default=0)
    n_recordings = db.Column(db.Integer, nullable=False, default=0)
    total_recording = db.Column(db.Float, nullable=False, default=0.00)
    passcode = db.Column(db.Boolean, nullable=False, default=0)
    researcher_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __repr__(self):
        return f"""\t\tStudy ID: {self.id}
        \tStudy Name: {self.study_name}
        \tNumber of Participants: {self.n_participants}
        \tNumber of Recordings: {self.n_recordings}
        \tTotal Recording Time: {self.total_recording}\n"""