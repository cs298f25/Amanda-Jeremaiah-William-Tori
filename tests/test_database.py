import sys
import os
# Add parent directory to path so we can import collector
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database
import pytest
import datetime
from unittest.mock import patch, MagicMock

# ============================================
# Testing Database Functions (No mocking needed)
# ============================================

#command to test- pytest tests/test_collector.py::test_init_db or pytest tests/ -v


def test_init_db():
    """Test that init_db creates the database tables."""
    database.init_db()
    
    # Verify tables exist by querying them
    import sqlite3
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        # Check Athletes table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Athletes'")
        assert cursor.fetchone() is not None
        # Check DailyMileage table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DailyMileage'")
        assert cursor.fetchone() is not None

def test_create_user():
    """Test that create_user creates a new user in the database."""
    #the issue is that the user is created once, so the test will fail if the user already exists


def test_create_duplicate_user():
    """Test that create_user creates a new user and prevents duplicates."""
    # Initialize database to ensure clean state
    database.init_db()
    
    # Test 1: Create a new user successfully
    database.create_user('testuser', 'testpassword', 1234567890, 'testaccess', 'testrefresh')
    
    # Verify user was created in the database
    import sqlite3
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", ('testuser',))
        user_row = cursor.fetchone()
        assert user_row is not None, "User should be created in database"
    
    with pytest.raises(ValueError, match="User already exists"):
        database.create_user('testuser', 'testpassword', 1234567890, 'testaccess', 'testrefresh')
    
    with sqlite3.connect(database.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", ('testuser',))
        count = cursor.fetchone()[0]
        assert count == 1, "Should only have one user with this username"
        
def test_check_if_user_exists():
    """Test that check_if_user_exists returns True if user exists, False if not."""
    assert database.check_if_user_exists('testuser') is True
    assert database.check_if_user_exists('nonexistentuser') is False

def test_user_login():
    """Test that user_login returns True if user exists and password is correct, False if not."""
    database.init_db()
    database.create_user('testuser', 'testpassword', 1234567890, 'testaccess', 'testrefresh')
    assert database.user_login('testuser', 'testpassword') is True
    assert database.user_login('testuser', 'wrongpassword') is False