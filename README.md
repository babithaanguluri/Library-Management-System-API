# 📚 Library Management System API

A RESTful backend API built using *Django* and *Django REST Framework* to manage books, members, borrowing transactions, overdue detection, and fine payments in a library.  
This application implements *state machines, **business rules, and **database relationships* required for real-world library operations.

---

# 1️ Project Overview

This API supports:

- Managing books and availability
- Registering and managing members
- Borrowing and returning books
- Overdue detection and fine calculation
- Member suspension and reactivation
- Tracking borrowed, returned, and overdue items

The backend ensures correct state transitions and enforces all library rules.

---

# 2️ Setup Instructions

Follow the steps below to run the project:

```bash
git clone https://github.com/babithaanguluri/Library-Management-System-API
cd Library-Management-System-API

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

