import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "MileageTracker.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        #Resetting the tables each time collector is run to maintain known state
        #these 3 lines will be commented out when we are done testing
        cursor.execute("DROP TABLE IF EXISTS Users")
        cursor.execute("DROP TABLE IF EXISTS DailyMileage")
        cursor.execute("DROP TABLE IF EXISTS Athletes")
        
        # User table
        cursor.execute("""
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
                       
            strava_athlete_id INTEGER UNIQUE,
            strava_access_token TEXT,
            strava_refresh_token TEXT,
            token_expiration INTEGER
        )
        """)

        # Athlete table
        cursor.execute("""
        CREATE TABLE Athletes (
            user_id INTEGER PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            gender TEXT CHECK(gender IN ('M', 'F', 'O')) DEFAULT 'O',
            mileage_goal REAL,
            long_run_goal REAL,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        """)

        # DailyMileage table
        cursor.execute("""
        CREATE TABLE DailyMileage (
            user_id INTEGER,
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            distance REAL,
            activity_title VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        """)

        conn.commit()

def get_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Unable to establish connection to {DB_NAME}")


# USER MANAGEMENT METHODS

def get_user_by_id(user_id):
    """Get user by ID. Returns row dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username):
    """Get user by username. Returns row dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username, password, strava_athlete_id, strava_access_token, strava_refresh_token):
    """Create a new user. Returns the new user's ID."""
    # Hash the password using werkzeug's secure hashing
    if check_if_user_exists(username):
        raise ValueError("User already exists")
    
    hashed_pw = generate_password_hash(password)
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO Users (username, password_hash, strava_athlete_id, strava_access_token, strava_refresh_token) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_pw, strava_athlete_id, strava_access_token, strava_refresh_token)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        # Handle race condition: two simultaneous requests could both pass existence check
        # The second INSERT will fail with IntegrityError due to UNIQUE constraint
        if 'UNIQUE constraint failed' in str(e) or 'username' in str(e).lower():
            raise ValueError("User already exists")
        else:
            # Re-raise if it's a different integrity constraint
            raise

def check_if_user_exists(username):
    """Check if a user exists in the database. Returns True/False."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def user_has_strava(user_id):
    """Check if user has Strava tokens. Returns True/False."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT strava_access_token FROM Users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None and row['strava_access_token'] is not None

def user_login(username, password):
    """Login a user. Returns True/False."""
    user_row = get_user_by_username(username)
    if user_row and check_password_hash(user_row['password_hash'], password):
        return True
    else:
        return False





# def save_user_tokens(user_id, tokens):
#     """Save Strava tokens to user. tokens is a dict with access_token, refresh_token, expires_at, athlete.id"""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """UPDATE Users 
#            SET strava_athlete_id = ?, 
#                strava_access_token = ?, 
#                strava_refresh_token = ?, 
#                token_expiration = ?
#            WHERE id = ?""",
#         (
#             tokens.get('athlete', {}).get('id'),
#             tokens.get('access_token'),
#             tokens.get('refresh_token'),
#             tokens.get('expires_at'),
#             user_id
#         )
#     )
#     conn.commit()
#     conn.close()


# ACTIVITY METHODS

# def get_activities_for_user(user_id):
#     """Get all activities for a user. Returns list of dicts."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """SELECT activity_id, date, distance, activity_title 
#            FROM DailyMileage 
#            WHERE user_id = ? 
#            ORDER BY date DESC""",
#         (user_id,)
#     )
#     rows = cursor.fetchall()
#     conn.close()
#     return [dict(row) for row in rows]

