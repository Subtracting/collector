import sys
from datetime import datetime, date
import sqlite3
from weather import get_weather


def initialise_db():
    conn = sqlite3.connect('stats.sqlite')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS stats (date DATE, subject TEXT, stat REAL, comment TEXT, weather REAL, humidity TEXT, wind REAL)')
    conn.commit()
    return cur, conn


def update_db(cur, conn, date, subject, stat, comment, weather, humidity, wind):

    variables = 'date, subject, stat, comment, weather, humidity, wind'

    cur.execute(f"""INSERT INTO stats({variables}) 
               VALUES (?,?,?,?,?,?,?);""", (date, subject, stat, comment, weather, humidity, wind))
    conn.commit()


def close_conn(conn):
    conn.close()


def logger(subject, date, stat, comment):
    cur, conn = initialise_db()

    today = date
    weather, humidity, wind = get_weather("Bergen op Zoom weather")

    update_db(cur, conn, today, subject, stat,
              comment, weather, humidity, wind)

    close_conn(conn)
