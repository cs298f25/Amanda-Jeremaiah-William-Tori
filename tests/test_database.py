import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database
import pytest
import datetime
from unittest.mock import patch, MagicMock


def test_init_db():
    """Test that init_db creates the database tables."""
    database.init_db()
    
    import sqlite3
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Athletes'")
        assert cursor.fetchone() is not None
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DailyMileage'")
        assert cursor.fetchone() is not None

def test_create_user():
    """Test that create_user creates a new user in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    user_row = cursor.fetchone()
    assert user_row is not None, "User should be created in database"
    assert database.get_user_by_username('testuser') is not None

def test_create_duplicate_user():
    """Test that create_user creates a new user and prevents duplicates."""
    database.init_db()
    
    database.create_user('testuser', 'testpassword')
    
    import sqlite3
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", ('testuser',))
        user_row = cursor.fetchone()
        assert user_row is not None, "User should be created in database"
    
    with pytest.raises(ValueError, match="User already exists"):
        database.create_user('testuser', 'testpassword')
    
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", ('testuser',))
        count = cursor.fetchone()[0]
        assert count == 1, "Should only have one user with this username"

def test_get_connection():
    """Test that the get_connection function returns a connection to the database."""
    conn = database.get_connection()
    assert conn is not None
    assert conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'").fetchone() is not None
    assert conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DailyMileage'").fetchone() is not None
    assert conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Athletes'").fetchone() is not None
    conn.close()

def test_update_last_sync_time_for_no_sync():
    """Test that the update_last_sync_time function updates the last sync time in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", ('testuser',))
    user_row = cursor.fetchone()
    assert user_row is not None
    assert user_row['last_sync_time'] == 0

def test_update_last_sync_time_for_sync():
    """Test that the update_last_sync_time function updates the last sync time in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    conn = database.get_connection()
    cursor = conn.cursor()
    database.update_last_sync_time(1)
    cursor.execute("SELECT * FROM Users WHERE username = ?", ('testuser',))
    user_row = cursor.fetchone()
    assert user_row is not None
    assert user_row['last_sync_time'] is not 0

def test_get_user_by_id():
    """Test that the get_user_by_id function returns the user by id."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    user_row = database.get_user_by_id(1)
    assert user_row is not None
    assert user_row['username'] == 'testuser'

def test_get_user_by_id_for_nonexistent_user():
    """Test that the get_user_by_id function returns None for a nonexistent user."""
    database.init_db()
    user_row = database.get_user_by_id(1)
    assert user_row is None

def test_get_user_by_username():
    """Test that the get_user_by_username function returns the user by username."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    user_row = database.get_user_by_username('testuser')
    assert user_row is not None
    assert user_row['username'] == 'testuser'

def test_get_user_by_username_for_nonexistent_user():
    """Test that the get_user_by_username function returns None for a nonexistent user."""
    database.init_db()
    user_row = database.get_user_by_username('nonexistentuser')
    assert user_row is None

def test_validate_password():
    """Test that the validate_password function returns True if the password is correct, False if not."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    assert database.validate_password('testuser', 'testpassword') is True
    assert database.validate_password('testuser', 'wrongpassword') is False

def test_validate_password_for_nonexistent_user():
    """Test that the validate_password function returns False if the user does not exist."""
    database.init_db()
    assert database.validate_password('nonexistentuser', 'testpassword') is False

def test_user_has_strava_before_authentication():
    """Test that the user_has_strava function returns True if the user has Strava tokens, False if not. Should only be true after authentication."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    assert database.user_has_strava(1) is False

def test_get_user_tokens_for_updated_tokens():
    """Test that the get_user_tokens function returns the user tokens."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.update_user_tokens(1, 'testaccesstoken', 'testrefreshtoken', 1717986911)
    tokens = database.get_user_tokens(1)
    assert tokens is not None
    assert tokens['strava_access_token'] is not None
    assert tokens['strava_refresh_token'] is not None
    assert tokens['token_expiration'] is not None

def test_get_user_tokens_for_first_time_tokens():
    """Test that the get_user_tokens function returns the user tokens."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.save_user_tokens_and_info(1, 'testaccesstoken', 'testrefreshtoken', 1717986911, 1234567890)
    tokens = database.get_user_tokens(1)
    assert tokens is not None
    assert tokens['strava_access_token'] is not None
    assert tokens['strava_refresh_token'] is not None
    assert tokens['token_expiration'] is not None

def test_get_tokens_for_nonexistent_user():
    """Test that the get_user_tokens function returns None for a nonexistent user."""
    database.init_db()
    tokens = database.get_user_tokens(1)
    assert tokens is None

def test_get_tokens_for_user_with_no_tokens():
    """Test that the get_user_tokens function returns None for a user with no tokens."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    tokens = database.get_user_tokens(1)
    assert tokens is not None
    assert tokens['strava_access_token'] is None
    assert tokens['strava_refresh_token'] is None
    assert tokens['token_expiration'] is None

def test_create_activity():
    """Test that the create_activity function creates an activity in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_activity(1, '2025-01-01', 10.0, 1234567890)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DailyMileage WHERE user_id = ? AND date = ? AND distance = ? AND activity_id = ?", (1, '2025-01-01', 10.0, 1234567890))
    activity_row = cursor.fetchone()
    assert activity_row is not None
    assert activity_row['distance'] == 10.0
    assert activity_row['activity_id'] == 1234567890

def test_create_activity_prevents_duplicate_activity():
    """Test that the create_activity function creates an activity in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_activity(1, '2025-01-01', 10.0, 1234567890)
    database.create_activity(1, '2025-01-01', 10.0, 1234567890)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DailyMileage WHERE user_id = ? AND date = ? AND distance = ? AND activity_id = ?", (1, '2025-01-01', 10.0, 1234567890))
    activity_row = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM DailyMileage WHERE user_id = ? AND date = ? AND distance = ? AND activity_id = ?", (1, '2025-01-01', 10.0, 1234567890))
    count = cursor.fetchone()[0]
    assert count == 1
    assert activity_row['distance'] == 10.0
    assert activity_row['activity_id'] == 1234567890

def test_create_athlete_with_goals():
    """Test that the create_athlete_with_goals function creates an athlete in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_athlete_with_goals(1, 100.0, 10.0)
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Athletes WHERE user_id = ?", (1,))
    athlete_row = cursor.fetchone()
    assert athlete_row is not None
    assert athlete_row['mileage_goal'] == 100.0
    assert athlete_row['long_run_goal'] == 10.0

def test_get_row_from_athletes_table():
    """Test that the get_row_from_athletes_table function returns the row from the athletes table."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_athlete_with_goals(1, 100.0, 10.0)
    row = database.get_row_from_athletes_table(1)
    assert row is not None
    assert row['mileage_goal'] == 100.0
    assert row['long_run_goal'] == 10.0

def test_get_row_from_athletes_table_for_nonexistent_user():
    """Test that the get_row_from_athletes_table function returns None for a nonexistent user."""
    database.init_db()
    row = database.get_row_from_athletes_table(1)
    assert row is None

def test_set_long_run_goal():
    """Test that the set_long_run_goal function updates the long run goal in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_athlete_with_goals(1, 100.0, 10.0)
    database.set_long_run_goal(1, 20.0)
    row = database.get_row_from_athletes_table(1)
    assert row is not None
    assert row['long_run_goal'] == 20.0

def test_set_mileage_goal():
    """Test that the set_mileage_goal function updates the mileage goal in the database."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_athlete_with_goals(1, 100.0, 10.0)
    database.set_mileage_goal(1, 200.0)
    row = database.get_row_from_athletes_table(1)
    assert row is not None
    assert row['mileage_goal'] == 200.0

def test_get_activities_for_user_one_activity():
    """Test that the get_activities_for_user function returns the activities for a user."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_activity(1, '2025-01-01', 10.0, 1234567890)
    activities = database.get_activities_for_user(1)
    assert activities is not None
    assert len(activities) == 1
    assert activities[0]['distance'] == 10.0
    assert activities[0]['activity_id'] == 1234567890

def test_get_activities_for_user_multiple_activities():
    """Test that the get_activities_for_user function returns the activities for a user."""
    database.init_db()
    database.create_user('testuser', 'testpassword')
    database.create_activity(1, '2025-01-01', 10.0, 1234567890)
    database.create_activity(1, '2025-01-02', 20.0, 1234567891)
    activities = database.get_activities_for_user(1)
    assert activities is not None
    assert len(activities) == 2
    assert activities[0]['distance'] == 20.0
    assert activities[1]['distance'] == 10.0
    assert activities[0]['activity_id'] == 1234567891
    assert activities[1]['activity_id'] == 1234567890