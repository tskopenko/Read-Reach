# Read-Reach


## Overview

> This project aims to create an online management system for book borrowings at the local library. The system provides features for tracking books, borrowings, users, and payments, making the borrowing process more efficient and user-friendly.

## Key Features

- **Inventory Management:** Easily track the availability of books in the library.
- **User-Friendly Interface:** Simple and intuitive interface for both administrators and users.
- **Payment Options:** Cash and credit card payment support for borrowings.
- **Automated Tracking:** Real-time tracking of book borrowings, due dates, and returns.
- **Reporting and Analytics:** Generate reports and gain insights into borrowing trends.
- **Notifications:** Receive notifications about due dates, overdue books, and payments.
- **Secure and Reliable:** Ensures data security and reliability for user information.

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/tskopenko/read-reach.git
   ```
2. Install dependencies:
   ```
   cd library-management-system
   pip install -r requirements.txt
   ```
3. Set up the database and run migrations:
   ```
   python manage.py migrate
   ```
4. Create a superuser for admin access:
   ```
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```
   python manage.py runserver
   ```
6. Access the admin dashboard at `http://127.0.0.1:8000/admin/` and log in with the superuser credentials.
7. Users can access the user portal at `http://127.0.0.1:8000/` to borrow books, make payments, and view borrowing history.

## Technologies Used

- Django: Web framework for backend development
- HTML, CSS, JavaScript: Frontend development
- PostgreSQL: Database management
- Bootstrap: Frontend styling and design

## Usage

- **Admin Dashboard:** Manage books, users, payments, and generate reports.
- **User Portal:** Borrow books, make payments, and view borrowing history.

## Contributors

- John Doe
- Jane Smith
