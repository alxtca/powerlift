# development start 10.01.2021 16:00

from app import app, db
from app.models import User, Workout


# set FLASK_APP=application.py
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Workout': Workout}


