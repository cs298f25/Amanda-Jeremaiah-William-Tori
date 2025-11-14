-- Schema for MileageTracker database

-- Athlete table
CREATE TABLE IF NOT EXISTS Athletes (
    athlete_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender TEXT CHECK(gender IN ('M', 'F', 'O')) DEFAULT 'O',
    mileage_goal REAL,
    long_run_goal REAL
);

-- DailyMileage table
CREATE TABLE IF NOT EXISTS DailyMileage (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    distance REAL,
    activity_title VARCHAR(100),
    athlete_id INTEGER,
    FOREIGN KEY (athlete_id) REFERENCES Athletes(athlete_id)
);

