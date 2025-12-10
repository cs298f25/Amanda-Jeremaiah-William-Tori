# API Documentation

This document outlines the routes and endpoints available in the Strava Mileage Tracker application.

## Frontend Routes
These routes return HTML templates and are intended for browser navigation.

### `GET /`
- **Description:** Main dashboard page.
- **Authentication:** Required (login_required)
- **Response:** Renders `index.html` template with user data.
- **Behavior:** Automatically syncs Strava data if last sync was more than 15 minutes ago.

### `GET /login`
- **Description:** Login page.
- **Authentication:** Not required.
- **Response:** Renders `login.html` template.

### `POST /login`
- **Description:** Authenticate user and create session.
- **Authentication:** Not required.
- **Request Body (form data):**
  - `username` (string): User's username.
  - `password` (string): User's password.
- **Response:** - Success: Redirects to dashboard (`/`).
  - Failure: Redirects to login page with error message.

### `GET /register`
- **Description:** Registration page.
- **Authentication:** Not required.
- **Response:** Renders `register.html` template.

### `POST /register`
- **Description:** Create new user account.
- **Authentication:** Not required.
- **Request Body (form data):**
  - `username` (string): Desired username (must be unique).
  - `password` (string): User's password (will be hashed).
  - `mileage` (float, optional): Weekly/monthly mileage goal.
  - `long_run` (float, optional): Long run distance goal.
- **Response:** - Success: Creates user, logs them in, redirects to dashboard.
  - Failure: Redirects to register page.

### `GET /logout`
- **Description:** Logout current user.
- **Authentication:** Required (login_required)
- **Response:** Logs out user and redirects to login page.

## Strava Integration Routes

### `GET /connect/strava`
- **Description:** Initiate Strava OAuth authorization flow.
- **Authentication:** Required (login_required)
- **Response:** Redirects user to Strava.com to authorize the application.

### `GET /strava/callback`
- **Description:** OAuth callback endpoint for Strava authorization.
- **Authentication:** Required (login_required)
- **Query Parameters:**
  - `code` (string): Authorization code from Strava (if successful).
  - `error` (string): Error code if authorization was denied.
- **Response:** - Success: Saves tokens, syncs activities, redirects to dashboard.
  - Failure: Redirects to dashboard with error message.

## JSON API Endpoints
These endpoints return JSON data and are used by the frontend JavaScript or external consumers.

### `GET /api/activities`
- **Description:** Get all activities, goals, and Strava connection status for the current user.
- **Authentication:** Required (login_required)
- **Response:** JSON object with the following structure:
  ```json
  {
    "activities": [
      {
        "activity_id": 123456789,
        "date": "2025-01-15",
        "distance": 5.2,
        "activity_title": "Morning Run"
      }
    ],
    "mileage_goal": 30.0,
    "long_run_goal": 8.0,
    "has_strava": true
  }

  
- **Response Fields:**
  - `activities` (array): List of activity objects, ordered by date (most recent first)
    - `activity_id` (integer): Strava activity ID
    - `date` (string): Activity date in YYYY-MM-DD format
    - `distance` (float): Distance in miles
    - `activity_title` (string): Title of the activity (may be "None")
  - `mileage_goal` (float): User's mileage goal
  - `long_run_goal` (float): User's long run goal
  - `has_strava` (boolean): Whether user has connected their Strava account

  