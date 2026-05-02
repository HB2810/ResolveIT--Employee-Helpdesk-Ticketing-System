# ResolveIT Employee Helpdesk Ticketing System

A production-style internal IT helpdesk application built with Flask, SQLite, SQLAlchemy, Flask-Login, Flask-WTF, Bootstrap 5, and Werkzeug password hashing.

Employees can register, sign in, create support tickets, view their own tickets, and track ticket progress. Admin users can view all tickets, update ticket status, set priority, add remarks, close tickets, and monitor dashboard statistics.

## Features

- Employee registration and login
- Secure password hashing
- Session management with Flask-Login
- Employee ticket creation and tracking
- Optional photo or video evidence upload while creating tickets
- Admin-only dashboard and ticket management
- Ticket statuses: Open, In Progress, Resolved, Closed
- Priority levels: Low, Medium, High, Critical
- Admin remarks for support updates
- Dashboard statistics
- Ticket Pulse scoring to surface urgent active tickets
- Admin search and priority/status filtering
- Bootstrap 5 responsive interface
- Form validation and CSRF protection
- Duplicate email prevention
- Sample admin account created automatically

## Tech Stack

- Python Flask
- SQLite
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Werkzeug
- HTML5, CSS3, Bootstrap 5

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Database Initialization

The SQLite database is initialized automatically on application startup. Running `python app.py` creates:

```text
database/helpdesk.db
```

It also creates all required database tables if they do not already exist.

## Sample Admin Account

The application creates a sample admin account automatically:

```text
Email: admin@example.com
Password: Admin@123
```

Use this account to access the admin dashboard and manage tickets.

## Folder Structure

```text
employee-helpdesk-system/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── uploads/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_ticket.html
│   ├── ticket_details.html
│   ├── admin_dashboard.html
│   ├── manage_tickets.html
│   └── error.html
│
├── models/
│   └── models.py
│
├── forms/
│   └── forms.py
│
├── routes/
│   └── routes.py
│
└── database/
    └── helpdesk.db
```

## Future Improvements

- Email notifications for ticket updates
- File attachments for tickets
- Admin user management screen
- Ticket category and department fields
- Search and advanced filtering
- Audit history for ticket changes
- REST API for mobile or external integrations
