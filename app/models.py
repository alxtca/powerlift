from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String(128))
    workouts = db.relationship('Workout', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    main_move = db.Column(db.String(100))
    main_move_reps = db.Column(db.Integer)
    main_move_sets = db.Column(db.Integer)
    main_move_rpe = db.Column(db.Integer)
    main_move_weight = db.Column(db.Integer)

    assa_move = db.Column(db.String(100))
    assa_move_reps = db.Column(db.Integer)
    assa_move_sets = db.Column(db.Integer)
    assa_move_rpe = db.Column(db.Integer)
    assa_move_weight = db.Column(db.Integer)

    assb1_move = db.Column(db.String(100))
    assb1_move_reps = db.Column(db.Integer)
    assb1_move_sets = db.Column(db.Integer)
    assb1_move_rpe = db.Column(db.Integer)
    assb1_move_weight = db.Column(db.Integer)

    assb2_move = db.Column(db.String(100))
    assb2_move_reps = db.Column(db.Integer)
    assb2_move_sets = db.Column(db.Integer)
    assb2_move_rpe = db.Column(db.Integer)
    assb2_move_weight = db.Column(db.Integer)

    assc1_move = db.Column(db.String(100))
    assc1_move_reps = db.Column(db.Integer)
    assc1_move_sets = db.Column(db.Integer)
    assc1_move_rpe = db.Column(db.Integer)
    assc1_move_weight = db.Column(db.Integer)

    assc2_move = db.Column(db.String(100))
    assc2_move_reps = db.Column(db.Integer)
    assc2_move_sets = db.Column(db.Integer)
    assc2_move_rpe = db.Column(db.Integer)
    assc2_move_weight = db.Column(db.Integer)

    note = db.Column(db.String(4000))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
