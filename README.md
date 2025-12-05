# MolWebAPI

## Overview
MolWebAPI is a Django REST Framework backend service designed for user authentication, course management, blog posts, and team member management. The API supports role-based access control with member, writer, and admin roles.

## Features

### Authentication & Authorization
- User registration with email, password, and profile information
- JWT-based authentication
- Email verification on signup
- Password reset functionality
- Role-based access control (Member, Writer, Admin)

### API Endpoints

#### Authentication (`/api/accounts/`)
- `POST /api/accounts/auth/register/` - User registration
- `POST /api/accounts/auth/token/` - JWT token obtain (login)
- `POST /api/accounts/auth/token/refresh/` - Refresh JWT token
- `POST /api/accounts/send-verification-email/` - Request verification email
- `POST /api/accounts/verify/<token>/` - Verify email
- `POST /api/accounts/send-password-reset-email/` - Request password reset
- `POST /api/accounts/reset-password/<token>/` - Reset password

#### Courses (`/api/course/`)
- `GET /api/course/` - List all courses (public, paginated)
- `GET /api/course/<id>/` - Get single course (public)
- `POST /api/course/create/` - Create course (admin only)
- `PUT /api/course/<id>/update/` - Update course (admin only)
- `DELETE /api/course/<id>/delete/` - Delete course (admin only)

#### Blog (`/api/blog/`)
- `GET /api/blog/` - List all blog posts (public, paginated)
- `GET /api/blog/<id>/` - Get single blog post (public)
- `POST /api/blog/create/` - Create blog post (writer/admin)
- `PUT /api/blog/<id>/update/` - Update blog post (writer own/admin any)
- `DELETE /api/blog/<id>/delete/` - Delete blog post (writer own/admin any)

#### Team (`/api/team/`)
- `GET /api/team/` - List all team members (public, paginated)
- `GET /api/team/<id>/` - Get single team member (public)
- `POST /api/team/create/` - Create team member (admin only)
- `PUT /api/team/<id>/update/` - Update team member (admin only)
- `DELETE /api/team/<id>/delete/` - Delete team member (admin only)

#### User Profile (`/api/user-profile/`)
- `GET /api/user-profile/user/profile/` - Get user profile
- `PUT /api/user-profile/user/profile/` - Update user profile
- `POST /api/user-profile/user/profile/` - Create user profile

## Technologies

- **Python 3.9+**
- **Django 4.2.19**
- **Django REST Framework 3.15.2**
- **djangorestframework-simplejwt** - JWT authentication
- **drf-spectacular** - API documentation
- **PostgreSQL** - Database
- **Gunicorn** - Production server
- **WhiteNoise** - Static file serving

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Mol.Domain.WebAPI
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your configuration:
   - `SECRET_KEY` - Django secret key
   - `DATABASE_URL` - PostgreSQL connection string
   - `SMTP_SEND_MAIL_URL` - SMTP API endpoint
   - `SMTP_API_KEY` - SMTP API key
   - `PORTAL_WEB_APP_URL` - Frontend application URL
   - `DEBUG` - Set to `True` for development

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access API documentation:**
   - Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/
   - ReDoc: http://127.0.0.1:8000/api/schema/redoc/

## Role-Based Access Control

### Member (Default)
- Can view all public content (courses, blog posts, team members)
- Cannot create, edit, or delete content

### Writer
- Can create blog posts
- Can edit and delete only their own blog posts
- Can view all public content

### Admin
- Full access to all operations
- Can create, edit, and delete courses, blog posts, and team members
- Can manage all content regardless of ownership

## Database Models

### User
- Email (unique)
- Hashed password
- Role (Member/Writer/Admin)
- Verification status

### UserProfile
- First name
- Last name
- Middle name (optional)
- Phone number (optional)
- Linked to User (OneToOne)

### Course
- Title
- Description
- URL
- Thumbnail URL

### BlogPost
- Title
- Description
- Body
- Date uploaded
- Created by (User)

### TeamMember
- Full name
- Occupation
- Bio
- Email URL
- LinkedIn URL

## Deployment

The project is configured for deployment on Railway. Key files:
- `Dockerfile` - Container configuration
- `Procfile` - Process configuration for Railway
- `requirements.txt` - Python dependencies

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile
3. Set environment variables in Railway dashboard
4. Deploy!

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Contributing

### How to Push Changes Using a Feature Branch

1. **Create a New Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes and Stage:**
   ```bash
   git add .
   ```

3. **Commit Your Changes:**
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

4. **Push Your Feature Branch:**
   ```bash
   git push -u origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Navigate to your repository on GitHub
   - Click "Compare & pull request" for your branch
   - Fill in the PR details and submit

6. **Review and Merge:**
   - After approval, changes will be merged
   - CI/CD pipeline will automatically deploy to production

## License

MIT License

## Support

For issues and questions, please contact the development team.

Here is the documentation in **Markdown (.md)** format exactly as you requested:

````md
# Project Setup Guide

This guide explains how to set up your Python virtual environment, install dependencies, and run database migrations.

---

## 1. Create a Virtual Environment

Use the following command to create a new virtual environment named **venv**:

```bash
python -m venv venv
````

---

## 2. Activate the Virtual Environment

After creating the environment, activate it:

### On Windows:

```bash
venv\Scripts\activate
```

### On macOS/Linux:

```bash
source venv/bin/activate
```

---

## 3. Install Required Packages

Make sure you have a `requirements.txt` file, then run:

```bash
pip install -r requirements.txt
```

---

## 4. Make Migrations

Generate migration files based on your Django models:

```bash
python manage.py makemigrations
```

---

## 5. Apply Migrations

Apply the migrations to your database:

```bash
python manage.py migrate
```

---

You're all set! 🎉

```
```

