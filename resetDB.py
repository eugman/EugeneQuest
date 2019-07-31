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

if os.path.exists("data/dailies.csv"):
    with open('data/dailies.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Daily(name=row[0],subtype=row[1],availableAfter=row[2],availableUntil=row[3],points=row[4],isWork=(row[5] == "True")))
            linecount += 1
app.db.session.commit()

if os.path.exists("data/foods.csv"):
    with open('data/foods.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Food(name=row[0],carbs = row[1]))
            linecount += 1
app.db.session.commit()


if os.path.exists("data/exercises.csv"):
    with open('data/exercises.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Exercise(name=row[0],reps=row[1],weight=row[2]))
            linecount += 1
app.db.session.commit()

if os.path.exists("data/items.csv"):
    with open('data/items.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                app.db.session.add(app.Item(name=row[0],cost=row[1]))
            linecount += 1
app.db.session.commit()

