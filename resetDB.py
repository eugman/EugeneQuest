import sys

if sys.version_info[0] < 3:
    print("Wrong Python version!")
    exit()

import app
import os
import csv

if os.path.exists("test.db"): 
    os.remove("test.db")
app.db.create_all()

app.db.session.add(app.Player(points=0))

if os.path.exists("dailies.csv"):
    with open('dailies.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Daily(name=row[0],subtype=row[1],availableAfter=row[2],availableUntil=row[3],points=row[4]))
            linecount += 1
app.db.session.commit()

if os.path.exists("foods.csv"):
    with open('foods.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Food(name=row[0],carbs = row[1]))
            linecount += 1
app.db.session.commit()


if os.path.exists("exercises.csv"):
    with open('exercises.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Exercise(name=row[0],reps=row[1],weight=row[2]))
            linecount += 1
app.db.session.commit()

