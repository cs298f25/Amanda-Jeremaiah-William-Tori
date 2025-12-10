# Workflow

We plan to fork the repository and work on our own version. Then we will add our changes to the shared repository. 

### Key Modules

#### `app.py`
Main Flask application file containing:
- Flask app initialization and configuration
- User authentication using Flask-Login
- Frontend route handlers (login, register, dashboard, logout)
- Strava OAuth integration routes
- API endpoint for activities data

**Key Classes:**
- `User`: UserMixin class for Flask-Login authentication

**Key Functions:**
- `load_user(user_id)`: Flask-Login user loader callback
- `dashboard()`: Main dashboard route with automatic sync logic
- `get_activities_data()`: API endpoint returning user activities and goals

#### `database.py`
Database operations module providing:
- SQLite database initialization and schema
- User management (create, authenticate, retrieve)
- Token encryption/decryption for Strava tokens
- Activity storage and retrieval
- Athlete goal management

**Key Functions:**
- `init_db()`: Creates database tables (Users, Athletes, DailyMileage)
- `encrypt_token(token)` / `decrypt_token(token)`: Secure token storage
- `create_user(username, password)`: Create new user with hashed password
- `validate_password(username, password)`: Verify user credentials
- `get_activities_for_user(user_id)`: Retrieve all activities for a user
- `save_user_tokens_and_info()`: Store encrypted Strava tokens

**Database Schema:**
- **Users**: id, username, password_hash, strava_athlete_id, strava_access_token, strava_refresh_token, token_expiration, last_sync_time
- **Athletes**: user_id (FK), mileage_goal, long_run_goal
- **DailyMileage**: user_id (FK), activity_id, date, distance, activity_title

#### `collector.py`
Strava API integration module handling:
- OAuth token exchange and refresh
- Activity fetching from Strava API
- Automatic token refresh when expired

**Key Functions:**
- `exchange_code_for_tokens(code)`: Exchange OAuth code for access/refresh tokens
- `authorize_and_save_user(code, user_id)`: Complete OAuth flow and save tokens
- `get_valid_access_token(user_id)`: Get valid access token, refreshing if needed
- `refresh_access_token(user_id, refresh_token)`: Refresh expired access token
- `fetch_and_save_user_data(user_id)`: Fetch last 30 days of activities from Strava and save to database

## Code Documentation

### Project Structure

```
Amanda-Jeremaiah-William-Tori/
├── app.py                 # Main Flask application and routes
├── database.py            # Database operations and SQLite management
├── collector.py           # Strava API integration and data collection
├── setup_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── MileageTracker.db      # SQLite database (created at runtime)
├── static/                # Static files (CSS, JavaScript)
│   ├── style.css
│   ├── script.js
│   ├── login_script.js
│   └── register_script.js
├── templates/             # HTML templates
│   ├── index.html
│   ├── login.html
│   └── register.html
└── tests/                 # Unit tests
    ├── conftest.py
    ├── test_database.py
    └── test_collector.py
```

### Key Modules

#### `app.py`
Main Flask application file containing:
- Flask app initialization and configuration
- User authentication using Flask-Login
- Frontend route handlers (login, register, dashboard, logout)
- Strava OAuth integration routes
- API endpoint for activities data

**Key Classes:**
- `User`: UserMixin class for Flask-Login authentication

**Key Functions:**
- `load_user(user_id)`: Flask-Login user loader callback
- `dashboard()`: Main dashboard route with automatic sync logic
- `get_activities_data()`: API endpoint returning user activities and goals

#### `database.py`
Database operations module providing:
- SQLite database initialization and schema
- User management (create, authenticate, retrieve)
- Token encryption/decryption for Strava tokens
- Activity storage and retrieval
- Athlete goal management

**Key Functions:**
- `init_db()`: Creates database tables (Users, Athletes, DailyMileage)
- `encrypt_token(token)` / `decrypt_token(token)`: Secure token storage
- `create_user(username, password)`: Create new user with hashed password
- `validate_password(username, password)`: Verify user credentials
- `get_activities_for_user(user_id)`: Retrieve all activities for a user
- `save_user_tokens_and_info()`: Store encrypted Strava tokens

**Database Schema:**
- **Users**: id, username, password_hash, strava_athlete_id, strava_access_token, strava_refresh_token, token_expiration, last_sync_time
- **Athletes**: user_id (FK), mileage_goal, long_run_goal
- **DailyMileage**: user_id (FK), activity_id, date, distance, activity_title

#### `collector.py`
Strava API integration module handling:
- OAuth token exchange and refresh
- Activity fetching from Strava API
- Automatic token refresh when expired

**Key Functions:**
- `exchange_code_for_tokens(code)`: Exchange OAuth code for access/refresh tokens
- `authorize_and_save_user(code, user_id)`: Complete OAuth flow and save tokens
- `get_valid_access_token(user_id)`: Get valid access token, refreshing if needed
- `refresh_access_token(user_id, refresh_token)`: Refresh expired access token
- `fetch_and_save_user_data(user_id)`: Fetch last 30 days of activities from Strava and save to database

### Security Features

- **Password Hashing**: Uses Werkzeug's `pbkdf2:sha256` method for secure password storage
- **Token Encryption**: Strava tokens are encrypted using Fernet (symmetric encryption) before storage
- **Session Management**: Flask-Login handles secure session management
- **SQL Injection Prevention**: All database queries use parameterized statements

### Data Sync Behavior

- Activities are automatically synced when:
  - User connects their Strava account for the first time
  - User visits dashboard and last sync was more than 15 minutes ago
- Activities are fetched from the last 30 days
- Up to 50 activities per sync (Strava API limit)
- Distance is converted from meters to miles for display

## Testing

Run tests using pytest:

```bash
pytest tests/
```

Test files:
- `test_database.py`: Database operation tests
- `test_collector.py`: Strava integration tests
- `test_app.py`: Flask endpoint tests

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- Flask 3.0.0 - Web framework
- Flask-Login 0.6.3 - User session management
- requests 2.31.0 - HTTP library for Strava API
- cryptography 42.0.5 - Token encryption
- python-dotenv 1.0.0 - Environment variable management
- gunicorn 23.0.0 - WSGI server for production