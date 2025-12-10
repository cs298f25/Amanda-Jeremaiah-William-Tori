import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import collector
import database

@pytest.fixture(autouse=True)
def mock_env_vars():
    fake_env = {
        'STRAVA_CLIENT_ID': 'test_id',
        'STRAVA_CLIENT_SECRET': 'test_secret',
        'ENCRYPTION_KEY': 'test_key'
    }
    with patch.dict(os.environ, fake_env):
        yield

def test_fetch_converts_meters_to_miles_correctly():
    user_id = 1
    
    fake_strava_data = [{
        'id': 101,
        'distance': 1609.34,         # ~1 mile
        'start_date_local': '2023-10-27T08:00:00Z',
        'name': 'Test Run'
    }]

    #patching for test
    with patch('requests.get') as mock_get, \
         patch('collector.get_valid_access_token') as mock_token, \
         patch('database.get_last_sync_time') as mock_sync_time, \
         patch('database.create_activity') as mock_db_save:
         
        mock_token.return_value = "fake_token"
        mock_sync_time.return_value = None
        
        # Setup fake network response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_strava_data
        mock_get.return_value = mock_response

        collector.fetch_and_save_user_data(user_id)

        mock_db_save.assert_called_with(
            user_id=1,
            date='2023-10-27',
            distance=1.0, 
            activity_id=101
        )


def test_authorize_and_save_user_parses_response():
    fake_code = "valid_code_123"
    user_id = 5
    
    fake_oauth_response = {
        'access_token': 'new_access',
        'refresh_token': 'new_refresh',
        'expires_at': 999999,
        'athlete': {
            'id': 888,
            'firstname': 'Fast',
            'lastname': 'Runner',
            'sex': 'M'
        }
    }

    with patch('collector.exchange_code_for_tokens') as mock_exchange, \
         patch('database.save_user_tokens_and_info') as mock_db_save:
         
        mock_exchange.return_value = fake_oauth_response

        collector.authorize_and_save_user(fake_code, user_id)

        mock_db_save.assert_called_once_with(
            user_id,
            'new_access',
            'new_refresh',
            999999,
            888
        )

def test_get_valid_access_token_refreshes_when_expired():
    """
    UNIT TEST: Verifies that if a token is expired, we trigger a refresh.
    """
    user_id = 1

    expired_tokens = {
        'strava_access_token': 'old_token',
        'strava_refresh_token': 'valid_refresh',
        'token_expiration': 1000 
    }

    with patch('database.get_user_tokens') as mock_get_tokens, \
         patch('collector.refresh_access_token') as mock_refresh_func:
         
        mock_get_tokens.return_value = expired_tokens
        mock_refresh_func.return_value = "brand_new_token"

        result = collector.get_valid_access_token(user_id)

        mock_refresh_func.assert_called_once_with(user_id, 'valid_refresh')
        assert result == "brand_new_token"

def test_get_valid_access_token_returns_existing_if_valid():
    """
    UNIT TEST: Verifies that if token is valid, we just return it 
    without refreshing.
    """
    import time
    user_id = 1
    
    future_time = int(time.time()) + 3600
    valid_tokens = {
        'strava_access_token': 'valid_token',
        'strava_refresh_token': 'valid_refresh',
        'token_expiration': future_time
    }

    with patch('database.get_user_tokens') as mock_get_tokens, \
         patch('collector.refresh_access_token') as mock_refresh_func:
         
        mock_get_tokens.return_value = valid_tokens

        result = collector.get_valid_access_token(user_id)

        mock_refresh_func.assert_not_called()
        assert result == "valid_token"