from app import app, db
from app.models import *
from app.config import *
import re

from flask import  render_template, request, Response
from flask_sqlalchemy import SQLAlchemy

@app.route('/increasecurrentexercise', methods=['GET', 'POST'])
def increase_current_exercise():
    allExercises = Exercise.query.filter(Exercise.name != "Running").filter(Exercise.name != "Treadmill - 3.1").filter(Exercise.name != "Mediate").order_by("rest", "completedLast").all()
    exercise = allExercises[0]

        
    exercise.completed = True
    exercise.completedLast = datetime.datetime.now()
    exercise.reps += exercise.interval
    exercise.rest = 3
    db.session.commit()

    addPoints(db, 2)



    return str(currentExercise.reps) + " " +currentExercise.name


@app.route('/currentexercise', methods=['GET', 'POST'])
def current_exercise():
    allExercises = Exercise.query.filter(Exercise.name != "Running").filter(Exercise.name != "Treadmill - 3.1").filter(Exercise.name != "Meditate").order_by("rest", "completedLast").all()
    currentExercise = allExercises[0]


    return str(currentExercise.reps) + " " +currentExercise.name

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    player = db.session.query(Player).get(1)

    result = request.form
    if result.get("increase"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.reps += exercise.interval
        exercise.rest = 3
        db.session.commit()

        addPoints(db, 2)

    if result.get("same"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.rest = 2
        db.session.commit()

        addPoints(db, 1)
    if result.get("decrease"):
        exercise_id = result.get("exercise_id")
        exercise = db.session.query(Exercise).get(exercise_id)   
        exercise.completed = True
        exercise.completedLast = datetime.datetime.now()
        exercise.reps -= exercise.interval
        exercise.rest = 3
        db.session.commit()

        addPoints(db, 1)




    allExercises = Exercise.query.order_by("rest", "completedLast").all()

    return render_template("exercise.html", exercises = allExercises, player = player)


