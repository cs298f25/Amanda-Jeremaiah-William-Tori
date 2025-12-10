import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 1. SETUP PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

def test_dashboard_triggers_sync_if_expired(client):
    """
    UNIT TEST: If sync time is old, verify collector is called.
    """
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True

    with patch('database.get_user_by_id') as mock_db_get:
        
        mock_db_get.return_value = {
            'id': 1, 
            'username': 'runner', 
            'last_sync_time': 0,
            'password_hash': 'ignore'
        }

        with patch('collector.fetch_and_save_user_data') as mock_collector, \
             patch('database.update_last_sync_time') as mock_db_update, \
             patch('database.user_has_strava', return_value=True):
            
            response = client.get('/')

            assert response.status_code == 200
            
            mock_collector.assert_called_once()
            
            mock_db_update.assert_called_once_with(1)

def test_login_failure_redirects_to_login(client):
    """
    UNIT TEST: Invalid login should redirect back to /login.
    """
    with patch('database.get_user_by_username') as mock_get, \
         patch('database.validate_password') as mock_val:
        
        mock_get.return_value = {'id': 1, 'username': 'test'}
        mock_val.return_value = False

        response = client.post('/login', data={'username': 'test', 'password': 'wrong'}, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location

def test_login_success_redirects_to_dashboard(client):
    """
    UNIT TEST: Valid credentials should redirect to the dashboard.
    """
    with patch('database.get_user_by_username') as mock_get, \
         patch('database.validate_password') as mock_val:
        
        mock_get.return_value = {
            'id': 1, 'username': 'runner', 'last_sync_time': 0, 'password_hash': 'h'
        }
        mock_val.return_value = True

        response = client.post('/login', data={'username': 'runner', 'password': 'correct'}, follow_redirects=False)

        # Should redirect (302) to the dashboard ('/')
        assert response.status_code == 302
        assert response.location == '/' or 'http://localhost/' in response.location

def test_register_creates_user_and_goals(client):
    """
    UNIT TEST: Registration should create a user and athlete record, then log them in.
    """
    with patch('database.create_user', return_value=55) as mock_create, \
         patch('database.create_athlete_with_goals') as mock_goals, \
         patch('database.get_user_by_id') as mock_get_id:
        
        mock_get_id.return_value = {'id': 55, 'username': 'new_user', 'last_sync_time': 0}

        response = client.post('/register', data={
            'username': 'new_user',
            'password': 'password123',
            'mileage': '100',
            'long_run': '20'
        }, follow_redirects=False)

        assert response.status_code == 302 
        
        mock_create.assert_called_once() 
        mock_goals.assert_called_with(55, 100.0, 20.0)

def test_api_returns_correct_json_structure(client):
    """
    UNIT TEST: The API should return the specific JSON format our frontend expects.
    """
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True

    with patch('database.get_user_by_id') as mock_db_get:
        mock_db_get.return_value = {'id': 1, 'username': 'runner', 'last_sync_time': 0}

        fake_activities = [{'activity_id': 101, 'distance': 5.0, 'date': '2023-01-01'}]
        fake_athlete = {'mileage_goal': 50.0, 'long_run_goal': 15.0}

        with patch('database.get_activities_for_user', return_value=fake_activities), \
             patch('database.get_row_from_athletes_table', return_value=fake_athlete), \
             patch('database.user_has_strava', return_value=True):

            response = client.get('/api/activities')
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['mileage_goal'] == 50.0
            assert data['activities'][0]['distance'] == 5.0
            assert data['has_strava'] is True

    