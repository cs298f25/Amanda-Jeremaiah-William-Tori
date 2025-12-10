# Strava Mileage Tracker

A web application for tracking running mileage and activities by integrating with the Strava API. Users can register, set mileage and long-run goals, connect their Strava account, and view their running activities in a personalized dashboard.

## Contributors
* Amanda McNesby
* Jeremiah Lezama
* William Kerr
* Tori Champagne

## Project Description

The Strava Mileage Tracker is a Flask-based web application that allows users to:
- Create user accounts with secure authentication
- Set personal mileage and long-run goals
- Connect their Strava account via OAuth 2.0
- Automatically sync running activities from Strava
- View their running activities and progress toward goals in a dashboard

The application uses SQLite for data storage, encrypts Strava tokens for security, and automatically refreshes access tokens when needed. Activities are synced from the last 30 days and displayed in a user-friendly interface.

## API Documentation

For detailed information on frontend routes, authentication flows, and JSON endpoints, please see the [API Documentation](documentation/api.md).

### Setup Instructions

For instructions on how to set up the environment, install dependencies, and deploy to production (AWS), please see the **[Deployment Guide](documentation/deploy.md)**.

### Developer Guide

For an overview of the codebase, project structure, key modules, and testing instructions, please see the **[Developer Guide](documentation/developers.md)**.

## License

This project is part of a web programming course assignment.
