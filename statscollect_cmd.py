import sys
from datetime import date
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from weather import get_weather

import os
def cls(): return os.system('cls')


def plot_sql(x_col, y_col, selection):
    plt.style.use('ggplot')

    df = pd.read_sql(
        f'SELECT * FROM STATS WHERE {y_col} = "{selection}"', conn)
    plt.bar(df[x_col], df['stat'])
    plt.title(f"{selection} by {x_col}")
    plt.show()


def initialise_db():
    conn = sqlite3.connect('stats.sqlite')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS stats (date DATE, subject TEXT, stat REAL, comment TEXT, weather REAL, humidity TEXT, wind REAL)')
    conn.commit()
    return cur, conn


def add_column_db(cur, conn, col_name):
    cur.execute(f'ALTER TABLE stats ADD COLUMN {col_name} TEXT;')
    conn.commit()


def delete_rows(cur, conn):
    cur.execute('DELETE FROM stats WHERE comment IN ("test");')
    conn.commit()


def update_db(cur, conn, date, subject, stat, comment, weather, humidity, wind):

    variables = 'date, subject, stat, comment, weather, humidity, wind'

    cur.execute(f"""INSERT INTO stats({variables}) 
               VALUES (?,?,?,?,?,?,?);""", (date, subject, stat, comment, weather, humidity, wind))
    conn.commit()


def close_conn(conn):
    conn.close()


cur, conn = initialise_db()

options = {"Reading": "# pages", "Sleep": "hours",
           "Euler": "# solved", "Drawing": "hours", "Mood": "1/10", "Running": "km", "Planking": "sec", "Movies": "rating (1/10)"}


def logger():
    cls()

    today = str(date.today())
    weather, humidity, wind = get_weather("Bergen op Zoom weather")

    for k in options.keys():
        print(f"* {k}")

    subject = input("Enter the stat you want to log...\n")
    if subject in options.keys():
        stat = input(f"What's the result ({options[subject]})? \n")
        comment = input("Do you want to add a comment? \n")

        print(f"Cool, you logged a {stat} for {subject}! \n")

        update_db(cur, conn, today,  subject, stat,
                  comment, weather, humidity, wind)

        again = input("Log another stat (Y/N)? \n")

        if again == "Y":
            cls()
            logger()
        else:
            sys.exit()
    else:
        print("Invalid input! Try again.")
        logger()


# logger()
# plot_sql("date", "subject", "Planking")

delete_rows(cur, conn)

close_conn(conn)
