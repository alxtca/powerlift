from app import db
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
from werkzeug.urls import url_parse
from datetime import date

idag = date.today()

# dummy data
all_workouts_list = ['Squat day. week#1, date: 11.01.21 ', 'Bench day. week#1, date: 11.01.21',
                     'Deadlift day. week#1, date: 11.01.21',
                     'Squat day. week#1, date: 11.01.21 ', 'Bench day. week#1, date: 11.01.21',
                     'Deadlift day. week#1, date: 11.01.21',
                     'Squat day. week#1, date: 11.01.21 ', 'Bench day. week#1, date: 11.01.21',
                     'Deadlift day. week#1, date: 11.01.21',
                     'Squat day. week#1, date: 11.01.21 ', 'Bench day. week#1, date: 11.01.21',
                     'Deadlift day. week#1, date: 11.01.21'
                     ]

# pick one
squat_assistance_a = ['Pause Squat', 'Box Squat', 'Super-Wide Box Squats', 'Close-Stance Squats', 'Front Squats',
                      'Sumo Deadlift (touch&go)', 'Piston Squats', 'Speed Squats', 'Form Squats', 'Front Pause Squats']
# pick two
squat_assistance_b = ['Glute-Ham Raise', 'Arched-Back Good Mornings', 'Leg Press', 'Goblet Squats',
                      'Single leg Good Morning', 'Piston Squats', 'Trap Bar deadlifts', 'Bulgarian split squat',
                      'Stationary lunge']
# pick 1-2
squat_assistance_c = ['Leg Extensions', 'Seated Leg Curls', 'Rolling Planks', 'Kettlebell Bottom-Up Carry',
                      'McGill Curl-Up', 'Stir the Pot', 'Bird Dog as a cool-down', 'Sled Drags', 'Prowler Sprints',
                      'Reverse Sled Drags']
# pick one
bench_assistance_a = ['Floor Press', 'Board Press', 'Close-Grip Press', 'Reverse Band Board Press',
                      'Standing Barbell or Dumbbell Overhead Press', 'Incline Barbell Press',
                      'Touch-and-Go Bench Press', 'Long Pause Presses(2s)', 'Speed bench', 'Form bench']
# pick two
bench_assistance_b = ['Traditional Dips', 'Bench Dips', 'Incline Dumbbell Press', 'Flat Dumbbell Press',
                      'JM Press', 'Skullcrushers']
# pick two
bench_assistance_c = ['Band Flyes', 'Bird Dog', 'McGill Crunch', 'Band Pushdowns', 'Hummer Curls',
                      'Reverse Barbell Curls', 'Push-ups', 'Piston Pushdowns', 'One-Arm Dumbbell Bench Press']
# pick one
deadlift_assistance_a = ['Block Pulls', 'Rack Pulls', 'Deficit Pulls', 'Opposite Stance Deadlift', 'Deadlift for reps',
                         'Pause Deadlifts', 'Arched-Back Good Mornings', 'Non-Rounded Back Stiff-Leg Deadlift',
                         'Speed Deadlifts', 'Form Deadlifts']
# pick two
deadlift_assistance_b = ['Barbell Rows', 'Rack barbell row with pause', 'Pull-up', 'McGill pull-up', 'Kroc Rows'
                         'Barbell or Dumbbell Shrugs', 'Chest-Supported Rows', 'Wide-Stance Box Squats',
                         'Close-Stance Squats', 'Pause Squats', 'Glute-Ham Raise', 'Leg Press', 'Front Pause Squats',
                         'Trap bar deadlifts']
# pick two
deadlift_assistance_c = ['Leg Extensions', 'Farmer Walk', 'Suitcase Carry', 'Kettlebell Bottoms-Up Carry',
                         'McGill Curl-UP', 'Stir the Pot', 'Bird Dog as cool-down', 'Sled Drags', 'Reverse Sled Drags']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/allworkouts')
def all_workouts():
    return render_template('all_workouts.html', allwork=all_workouts_list)


@app.route('/select')
def select():
    # check last performed workout in db and render a message
    u = User.query.filter_by(username=current_user.username)
    return render_template('select.html')


# Redirect here after successful login
@app.route('/logs')
def logs():
    return render_template('logs.html')


@app.route('/form', methods=['POST', 'GET'])
def form():
    if request.method == 'GET':
        # message = 'You need to select workout on selection page before accessing this page'
        # return render_template('error.html', message=message)
        return redirect(url_for('select'))
    move = request.form.get('movement')
    week = request.form.get('week')
    training_type = request.form.get('season')  # atm only off-season chart is available

    # check what day is selected. Based on that send appropriate assistance exercises lists to html form:
    if move == 'Squat':
        assistance_a = squat_assistance_a
        assistance_b = squat_assistance_b
        assistance_c = squat_assistance_c
    elif move == 'Bench Press':
        assistance_a = bench_assistance_a
        assistance_b = bench_assistance_b
        assistance_c = bench_assistance_c
    elif move == 'Deadlift':
        assistance_a = deadlift_assistance_a
        assistance_b = deadlift_assistance_b
        assistance_c = deadlift_assistance_c
    elif move == 'Buff&Fluff' and training_type == 'Offseason':
        return render_template('buff_form.html')
    else:
        assistance_a = ['Error']
        assistance_b = ['Error']
        assistance_c = ['Error']
    if training_type == 'Offseason':
        # check if any workout has been logged before.

        return render_template('form.html', move=move, week=week, assistance_a=assistance_a, assistance_b=assistance_b,
                               assistance_c=assistance_c, idag=idag)
    elif training_type == 'Pre-Contest':
        message = 'Pre-contest charts have not been developed yet'
        return render_template('error.html', message=message)
    else:
        message = 'Unknown Error'
        return render_template('error.html', message=message)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # to redirect back to page attempted to access before login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
