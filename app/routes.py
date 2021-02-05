from app import db
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Workout
from werkzeug.urls import url_parse
from datetime import date

idag = date.today()

# Lists with all exercises:
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


@app.route('/log_display/<int:work_id>')
@login_required
def log_display(work_id):
    w = Workout.query.get(int(work_id))
    return render_template('logged_workout.html', w=w)


@app.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    w_logs = Workout.query.order_by(Workout.id.desc()).filter(Workout.user_id == current_user.id).\
        paginate(page=page, per_page=5)
    return render_template('logs.html', w_logs=w_logs)


@app.route('/select')
@login_required
def select():
    # select last performed workout for this user:
    w = Workout.query.order_by(Workout.id.desc()).filter(Workout.user_id == current_user.id).first()

    # catch errors if user never had a workout logged.
    if w is not None:
        if w.main_move == 'Squat':
            main_move_today = 'Bench Press'
            week = int(w.week)
        elif w.main_move == 'Bench Press':
            main_move_today = 'Deadlift'
            week = int(w.week)
        else:
            main_move_today = 'Squat'
            week = int(w.week)+1
        if w.training_type == 'Offseason':
            training_type = 'Offseason'

    if w is None:
        main_move_today = None
        week = None
        training_type = None

    if week == 11:
        week = 1

    return render_template('select.html', w=w, main_move_today=main_move_today, week=week, training_type=training_type)


@app.route('/form', methods=['POST', 'GET'])
@login_required
def form():
    # shall not be possible to access this form without selecting correct values first:
    if request.method == 'GET':
        # message = 'You need to select workout on selection page before accessing this page'
        # return render_template('error.html', message=message)
        return redirect(url_for('select'))

    move = request.form.get('movement')
    week = int(request.form.get('week'))
    training_type = request.form.get('season')

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
    # Offseason charts:
    if training_type == 'Offseason':

        # Set correct sets, reps, RPE for every week#
        if week == 1:
            main_move_reps = 5
            main_move_sets = 5
            main_move_rpe = 6
            assa_move_reps = 6
            assa_move_sets = 2
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 12
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 2:
            main_move_reps = 4
            main_move_sets = 4
            main_move_rpe = 6
            assa_move_reps = 6
            assa_move_sets = 3
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 12
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 3:
            main_move_reps = 1
            main_move_sets = 5
            main_move_rpe = 5
            assa_move_reps = 6
            assa_move_sets = 2
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 15
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 4:
            main_move_reps = 3
            main_move_sets = 3
            main_move_rpe = 7
            assa_move_reps = 6
            assa_move_sets = 4
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 12
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 5:
            main_move_reps = 5
            main_move_sets = 5
            main_move_rpe = 7
            assa_move_reps = 4
            assa_move_sets = 4
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 4
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 12
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 6:
            main_move_reps = 1
            main_move_sets = 5
            main_move_rpe = 7
            assa_move_reps = 4
            assa_move_sets = 2
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 15
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 7:
            main_move_reps = 4
            main_move_sets = 4
            main_move_rpe = 7
            assa_move_reps = 4
            assa_move_sets = 4
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 8:
            main_move_reps = 3
            main_move_sets = 3
            main_move_rpe = 7
            assa_move_reps = 4
            assa_move_sets = 4
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 3
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 3
            assc1_move_rpe = assc2_move_rpe = 8

        elif week == 9:
            main_move_reps = 1
            main_move_sets = 5
            main_move_rpe = 7
            assa_move_reps = 2
            assa_move_sets = 2
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 2
            assb1_move_rpe = assb2_move_rpe = 8
            assc1_move_reps = assc2_move_reps = 15
            assc1_move_sets = assc2_move_sets = 2
            assc1_move_rpe = assc2_move_rpe = 8

        else:
            main_move_reps = 1
            main_move_sets = 1
            main_move_rpe = 5
            assa_move_reps = 2
            assa_move_sets = 2
            assa_move_rpe = 7
            assb1_move_reps = assb2_move_reps = 10
            assb1_move_sets = assb2_move_sets = 2
            assb1_move_rpe = assb2_move_rpe = 7
            assc1_move_reps = assc2_move_reps = 12
            assc1_move_sets = assc2_move_sets = 2
            assc1_move_rpe = assc2_move_rpe = 7

        # check if workout of similar type has been logged before.
        w = Workout.query.order_by(Workout.id.desc()).filter(Workout.user_id == current_user.id).\
            filter(Workout.main_move == move).first()
        if w is None:  # First training/week ever
            return render_template('form.html', move=move, week=week, idag=idag, assistance_a=assistance_a,
                                   assistance_b=assistance_b, assistance_c=assistance_c, training_type=training_type,
                                   main_move_reps=main_move_reps, main_move_sets=main_move_sets, main_move_rpe=main_move_rpe,
                                   assa_move_rpe=assa_move_rpe, assa_move_sets=assa_move_sets, assa_move_reps=assa_move_reps,
                                   assb1_move_rpe=assb1_move_rpe, assb1_move_sets=assb1_move_sets, assb1_move_reps=assb1_move_reps,
                                   assb2_move_rpe=assb2_move_rpe, assb2_move_sets=assb2_move_sets, assb2_move_reps=assb2_move_reps,
                                   assc1_move_rpe=assc1_move_rpe, assc1_move_sets=assc1_move_sets, assc1_move_reps=assc1_move_reps,
                                   assc2_move_rpe=assc2_move_rpe, assc2_move_sets=assc2_move_sets, assc2_move_reps=assc2_move_reps)

        return render_template('form.html', move=move, week=week, assistance_a=assistance_a, assistance_b=assistance_b,
                               assistance_c=assistance_c, idag=idag, training_type=training_type, w=w,
                               main_move_reps=main_move_reps, main_move_sets=main_move_sets,
                               main_move_rpe=main_move_rpe,
                               assa_move_rpe=assa_move_rpe, assa_move_sets=assa_move_sets,
                               assa_move_reps=assa_move_reps,
                               assb1_move_rpe=assb1_move_rpe, assb1_move_sets=assb1_move_sets,
                               assb1_move_reps=assb1_move_reps,
                               assb2_move_rpe=assb2_move_rpe, assb2_move_sets=assb2_move_sets,
                               assb2_move_reps=assb2_move_reps,
                               assc1_move_rpe=assc1_move_rpe, assc1_move_sets=assc1_move_sets,
                               assc1_move_reps=assc1_move_reps,
                               assc2_move_rpe=assc2_move_rpe, assc2_move_sets=assc2_move_sets,
                               assc2_move_reps=assc2_move_reps
                               )

    elif training_type == 'Pre-Contest':
        message = 'Pre-contest charts have not been implemented yet. Please select Offseason.'
        return render_template('error.html', message=message)
    else:
        message = 'Unknown Error'
        return render_template('error.html', message=message)


@app.route('/form_save', methods=['POST', 'GET'])
@login_required
def form_save():
    if request.method == 'GET':
        return redirect(url_for('index'))

    week = request.form.get('week')
    training_type = request.form.get('training_type')

    main_move = request.form.get('mm')
    main_move_reps = request.form.get('mm_reps')
    main_move_sets = request.form.get('mm_sets')
    main_move_rpe = request.form.get('mm_rpee')
    main_move_weight = request.form.get('mm_weig')

    assa_move = request.form.get('ae_a')
    assa_move_reps = request.form.get('ae_a_reps')
    assa_move_sets = request.form.get('ae_a_sets')
    assa_move_rpe = request.form.get('ae_a_rpee')
    assa_move_weight = request.form.get('ae_a_weig')

    assb1_move = request.form.get('ae_b1')
    assb1_move_reps = request.form.get('ae_b1_reps')
    assb1_move_sets = request.form.get('ae_b1_sets')
    assb1_move_rpe = request.form.get('ae_b1_rpee')
    assb1_move_weight = request.form.get('ae_b1_weig')

    assb2_move = request.form.get('ae_b2')
    assb2_move_reps = request.form.get('ae_b2_reps')
    assb2_move_sets = request.form.get('ae_b2_sets')
    assb2_move_rpe = request.form.get('ae_b2_rpee')
    assb2_move_weight = request.form.get('ae_b2_weig')

    assc1_move = request.form.get('ae_c1')
    assc1_move_reps = request.form.get('ae_c1_reps')
    assc1_move_sets = request.form.get('ae_c1_sets')
    assc1_move_rpe = request.form.get('ae_c1_rpee')
    assc1_move_weight = request.form.get('ae_c1_weig')

    assc2_move = request.form.get('ae_c2')
    assc2_move_reps = request.form.get('ae_c2_reps')
    assc2_move_sets = request.form.get('ae_c2_sets')
    assc2_move_rpe = request.form.get('ae_c2_rpee')
    assc2_move_weight = request.form.get('ae_c2_weig')

    note = request.form.get('daynotes')

    user_id = current_user.id

    w = Workout(main_move=main_move, main_move_reps=main_move_reps, main_move_sets=main_move_sets,
                main_move_rpe=main_move_rpe, main_move_weight=main_move_weight,
                assa_move=assa_move, assa_move_reps=assa_move_reps, assa_move_sets=assa_move_sets,
                assa_move_rpe=assa_move_rpe, assa_move_weight=assa_move_weight,
                assb1_move=assb1_move, assb1_move_sets=assb1_move_sets, assb1_move_reps=assb1_move_reps,
                assb1_move_rpe=assb1_move_rpe, assb1_move_weight=assb1_move_weight,
                assb2_move=assb2_move, assb2_move_sets=assb2_move_sets, assb2_move_reps=assb2_move_reps,
                assb2_move_rpe=assb2_move_rpe, assb2_move_weight=assb2_move_weight,
                assc1_move=assc1_move, assc1_move_sets=assc1_move_sets, assc1_move_reps=assc1_move_reps,
                assc1_move_rpe=assc1_move_rpe, assc1_move_weight=assc1_move_weight,
                assc2_move=assc2_move, assc2_move_sets=assc2_move_sets, assc2_move_reps=assc2_move_reps,
                assc2_move_rpe=assc2_move_rpe, assc2_move_weight=assc2_move_weight,
                note=note, user_id=user_id, week=week, training_type=training_type)
    db.session.add(w)
    db.session.commit()
    flash('Workout has been saved')
    return render_template('index.html')


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
