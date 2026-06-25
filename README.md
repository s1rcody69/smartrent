# SmartRent

A full-stack property management and rent collection system for landlords and tenants in Kenya, with real M-Pesa Daraja payment integration.

## Overview

SmartRent is built around the idea of a **centralized platform for property management** that replaces the spreadsheets, paper records, and WhatsApp messages most Kenyan landlords currently rely on. Instead of managing properties, tenants, rent, and maintenance across fragmented channels, landlords and tenants interact through one secure, role-based system.

The backend is a **Django REST Framework API** with JWT authentication, role-based access control across three user types (Admin, Landlord, Tenant), and a real **Safaricom M-Pesa STK Push** payment flow — all backed by PostgreSQL and deployed live on Render.

## Features

### Authentication
- Custom User model using email (not username) for login, with UUID primary keys
- JWT authentication via SimpleJWT — short-lived access tokens, longer-lived refresh tokens with rotation and blacklisting on logout
- Role-based access: `admin`, `landlord`, `tenant`, each with a distinct permission scope
- Automatic `LandlordProfile` / `TenantProfile` creation on registration, one-to-one with `User`

### Property Management (CRUD)
- Landlords can:
  - Create, update, and delete properties (apartment, house, bedsitter, or commercial)
  - Add units within each property, each with its own rent amount, bedrooms, bathrooms, and type
  - Upload a cover image per property (stored via Cloudinary), or select from curated stock images
- Tenants can browse all active properties available for lease
- Filtering, search, and ordering supported on all list endpoints
- Role-scoped querysets — landlords only ever see their own properties; tenants only see active listings

### Lease Management (CRUD)
- Landlords assign a tenant to a vacant unit, creating a lease with a locked-in rent amount, deposit, and start/end date
- A lease's `save()` method automatically flips the linked unit's status between `vacant` and `occupied` — this business rule lives on the model, not the view, so it fires identically regardless of entry point (API, Django admin, or script)
- Rent amount is captured at signing and stored independently of the unit's current market rate, preserving historical accuracy if rent is later raised for new tenants
- Tenants can only view their own lease; landlords only see leases on their own properties

### Maintenance Requests (CRUD)
- Tenants submit requests with a title, description, category, and priority
- The unit and tenant are derived automatically from the tenant's active lease — never accepted as raw input — so a tenant can never submit a request against a unit they don't occupy
- Landlords update status through a defined workflow: `pending → assigned → in_progress → completed`
- Supports image upload as evidence of the reported issue

### Payments — M-Pesa Integration
- Real Safaricom Daraja STK Push integration (sandbox), sending a genuine PIN prompt to the tenant's phone
- Rent invoices generated per lease, per month, with `pending`, `paid`, and `overdue` states
- A public, unauthenticated webhook endpoint receives Safaricom's payment confirmation callback and reconciles the result against the original transaction
- `Payment` (gateway-agnostic record) is kept separate from `MpesaTransaction` (raw Safaricom response data), preserving a full audit trail without polluting the core payment model with gateway-specific fields
- On successful payment, the linked invoice is automatically marked paid

### Reports & Analytics
- Revenue report with monthly breakdown, outstanding balances, and overdue totals
- Occupancy report, platform-wide and broken down per property
- Payment and maintenance statistics, including recent payment history
- A combined dashboard summary endpoint for at-a-glance metrics
- Restricted to `admin` and `landlord` roles — tenants have no access to aggregate financial data

### Admin Panel
- Full Django admin integration for every model — users, profiles, properties, units, leases, invoices, payments, and maintenance requests
- Custom list displays, filters, and search fields configured per model for efficient platform oversight

## Tech Stack

### Backend
- Django 6.0
- Django REST Framework
- djangorestframework-simplejwt (JWT authentication, token blacklisting)
- django-filter (filtering, search, ordering)
- django-cors-headers

### Database
- PostgreSQL (local development and production)
- `dj-database-url` for environment-aware connection configuration

### Media & Payments
- Cloudinary (property and maintenance image storage)
- Safaricom Daraja API (M-Pesa STK Push, sandbox)

### Deployment
- Render (web service + managed PostgreSQL)
- Gunicorn (production WSGI server)

## Live Deployment

Backend: `https://smartrent-l1c0.onrender.com`

## Running the Project Locally

Follow these steps to set up and run the backend on your local machine.

### Prerequisites

Make sure you have the following installed:
- Python 3.12+
- PostgreSQL
- pip and virtualenv
- Git

### 1. Clone the Repository

    git clone https://github.com/s1rcody69/smartrent.git
    cd smartrent/backend

### 2. Create and Activate a Virtual Environment

    virtualenv venv
    source venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Setup Environment Variables

Create a `.env` file inside the `backend/` directory and add:

    SECRET_KEY=your-django-secret-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    DB_NAME=smartrent_db
    DB_USER=smartrent_user
    DB_PASSWORD=your-db-password
    DB_HOST=localhost
    DB_PORT=5432

    CLOUDINARY_CLOUD_NAME=your-cloud-name
    CLOUDINARY_API_KEY=your-api-key
    CLOUDINARY_API_SECRET=your-api-secret

    MPESA_CONSUMER_KEY=your-consumer-key
    MPESA_CONSUMER_SECRET=your-consumer-secret
    MPESA_SHORTCODE=174379
    MPESA_PASSKEY=your-passkey
    MPESA_CALLBACK_URL=https://your-ngrok-url/api/payments/mpesa/callback/

> Do not commit your `.env` file. It is already included in `.gitignore`.

### 5. Setup PostgreSQL

1. Create a database user and database matching your `.env` values:

    ```
    sudo -u postgres psql
    CREATE USER smartrent_user WITH PASSWORD 'your-db-password';
    CREATE DATABASE smartrent_db OWNER smartrent_user;
    GRANT ALL PRIVILEGES ON DATABASE smartrent_db TO smartrent_user;
    ```

2. Run migrations:

    ```
    python manage.py migrate
    ```

3. Create a superuser:

    ```
    python manage.py createsuperuser
    ```

### 6. Setup M-Pesa Sandbox (Optional, for Payment Testing)

1. Register a sandbox app at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Use shortcode `174379` and the public sandbox passkey for testing
3. Expose your local server with ngrok so Safaricom can reach your callback URL:

    ```
    ngrok http 8000
    ```

4. Update `MPESA_CALLBACK_URL` in `.env` with the ngrok HTTPS URL

### 7. Run the Development Server

    python manage.py runserver

### 8. Open in Browser / Postman

    http://127.0.0.1:8000/admin/        — Django admin
    http://127.0.0.1:8000/api/          — API root

### 9. Test the App Flow

- Register a landlord and a tenant via `POST /api/auth/register/`
- Log in as the landlord, create a property and a unit
- Create a lease assigning the tenant to that unit — confirm the unit status flips to `occupied`
- Log in as the tenant, submit a maintenance request — confirm the unit is derived automatically from their lease
- Create a rent invoice, trigger an M-Pesa STK Push, and confirm the invoice is marked paid after entering the PIN
- View the dashboard summary and revenue reports as the landlord

### Common Issues

**1. `AUTH_USER_MODEL` errors on migrate**
- The custom `User` model must be configured before the very first migration. If you see inconsistent migration history, drop and recreate the database, delete migration files (except `__init__.py`), and re-run `migrate` from a clean state.

**2. CORS errors from the frontend**
- Confirm `CORS_ALLOWED_ORIGINS` in `settings.py` includes your frontend's actual origin (e.g. `http://localhost:5173` for Vite), not a placeholder or wrong port.

**3. M-Pesa STK Push not arriving on phone**
- Confirm `MPESA_CALLBACK_URL` in `.env` matches your current ngrok URL exactly — ngrok's free tier issues a new URL every time it restarts.
- Confirm your Daraja consumer key/secret and passkey are correct for the sandbox environment.

**4. `ProtectedError` when deleting a unit or lease**
- This is expected behavior, not a bug — units with an active lease, and leases with invoices, are protected from deletion to preserve financial history. Terminate the lease or settle the invoice first.

**5. Permission denied (403) on an endpoint**
- Confirm you are logged in as the correct role — most write endpoints are restricted to `landlord` or `admin`, and list endpoints are scoped so each role only sees their own data.