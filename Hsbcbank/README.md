
# Credit Card Statement Generator

A Flask-based web application that generates credit card statements in PDF format with multi-language support (English, Tamil, Hindi).

## Live Demo
Try it live at [https://hsbcbackend01.replit.app](https://hsbcbackend01.replit.app)

## Tech Stack
- **Backend**: Python/Flask
- **Database**: SQLite/PostgreSQL
- **PDF Generation**: ReportLab
- **Frontend**: HTML/CSS with Bootstrap
- **Server**: Gunicorn

## Features
- Multi-language statement generation (EN, TA, HI)
- PDF generation with custom fonts
- Transaction history display
- Performance logging
- Database integration
- RESTful API endpoints

## Dependencies
```
Flask
Flask-Cors
SQLAlchemy
reportlab
gunicorn
```

## Setup
1. Clone this Repl
2. The environment will automatically install required packages
3. Click the Run button to start the application
4. Access the application at the provided URL

## API Endpoints
- `/` - Main application interface
- `/api/generate-statement` - Generate PDF statement
- `/api/languages` - Get supported languages
- `/preview-statement` - Preview statement before generation
- `/download-statement/<id>` - Download generated statement

## Environment Variables
- `DATABASE_URL` - Database connection string (optional, defaults to SQLite)
- `SESSION_SECRET` - Required for session management
- `FLASK_ENV` - Application environment (development/production)

## Development
The application runs on port 5000 and is configured for both development and production environments through Gunicorn.
