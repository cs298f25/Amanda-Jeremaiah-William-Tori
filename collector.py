# collector.py
import sqlite3
import datetime
import random
import os

DB_NAME = "MileageTracker.db"
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        #Resetting the tables each time collector is run to maintain known state
        cursor.execute("DROP TABLE IF EXISTS DailyMileage")
        cursor.execute("DROP TABLE IF EXISTS Athletes")
        
        # Read and execute schema from SQL file
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)

        conn.commit()

def add_example_data():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            athletes = [
                ("John", "Smith", "M", 30.0, 8.0)
            ]

            athlete_ids = []
            for athlete in athletes:
                cursor.execute("INSERT INTO Athletes (first_name, last_name, gender, mileage_goal, long_run_goal) VALUES (?,?,?,?,?)", athlete)

                athlete_ids.append(cursor.lastrowid)

            base_time = datetime.datetime.now()

            for athlete_id in athlete_ids:
                for i in range(7):
                    day = base_time - datetime.timedelta(days = i)
                    dist = round(random.uniform(3.0, 10.0), 2)
                    title = "None"

                    cursor.execute(
                        "INSERT INTO DailyMileage (date, distance, activity_title, athlete_id) VALUES (?, ?, ?, ?)",
                        (day.date(), dist, title, athlete_id)
                    )

            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    init_db()
    add_example_data()
    print("---")
    print("Collector finished. You can now run app.py")