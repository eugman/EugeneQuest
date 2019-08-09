import sys

if sys.version_info[0] < 3:
    print("Wrong Python version!")
    exit()

from app import  db
from app.models import *
import os
import csv

if os.path.exists("test.db"): 
    os.remove("test.db")
db.create_all()

db.session.add(Player(points=0))

if os.path.exists("data/dailies.csv"):
    with open('data/dailies.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Daily(name=row[0],subtype=row[1],availableAfter=row[2],availableUntil=row[3],points=row[4],isWork=(row[5] == "True"),restDuration=row[6]))
            linecount += 1
db.session.commit()

if os.path.exists("data/foods.csv"):
    with open('data/foods.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Food(name=row[0],carbs = row[1]))
            linecount += 1
db.session.commit()

if os.path.exists("data/books.csv"):
    with open('data/books.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Book(name=row[0],pages = row[1], current = row[2]))
            linecount += 1
db.session.commit()


if os.path.exists("data/goals.csv"):
    with open('data/goals.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Goal(name=row[0],category = row[1], start = row[2], end=row[3],reversedScale=(row[4]=="True"),current=row[5]))
            linecount += 1
db.session.commit()



if os.path.exists("data/exercises.csv"):
    with open('data/exercises.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Exercise(name=row[0],reps=row[1],weight=row[2]))
            linecount += 1
db.session.commit()

if os.path.exists("data/items.csv"):
    with open('data/items.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        linecount = 0
        for row in spamreader:
            if linecount > 0:
                db.session.add(Item(name=row[0],cost=row[1],url=row[2]))
            linecount += 1
db.session.commit()

