# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Grupo Master is a Django-based welder qualification management system (Sistema de Qualificação de Soldadores). The application manages welder certifications, qualifications, and related documentation for companies.

## Key Architecture

### Django Project Structure
- **grupoMaster/**: Main Django project configuration
  - `settings.py`: Development settings (SQLite, DEBUG=True)
  - `settings_production.py`: Production settings (PostgreSQL, security headers, logging)
- **raqs/**: Main application handling welder qualification requests
  - Custom user model: `Operador` extends `AbstractEmpresaUser`
  - Key models: `Soldador`, `Empresa`, `RAQS`, `CQS`, various test models
  - Uses HTMX for dynamic frontend interactions

### Database Configuration
- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (configured via environment variables)
- Custom AUTH_USER_MODEL: `raqs.Operador`

### Frontend Stack
- **CSS Framework**: Bulma (via npm/sass compilation)
- **JavaScript**: HTMX for dynamic interactions
- **Templates**: Django templates with partials in `raqs/templates/partials/`

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Bulma/Sass)
npm install
```

### Database Operations
```bash
# Development (SQLite)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Production (PostgreSQL)
python manage.py migrate --settings=grupoMaster.settings_production
python manage.py createsuperuser --settings=grupoMaster.settings_production
python manage.py collectstatic --noinput --settings=grupoMaster.settings_production
```

### Frontend Build
```bash
# Build Bulma CSS once
npm run build-bulma

# Watch mode for development
npm start
```

### Testing
- Uses Django's built-in testing framework
- Test files: `raqs/tests.py` (currently minimal)
- Run tests: `python manage.py test`

## Deployment

### Local Development
```bash
python manage.py runserver
# Access at http://127.0.0.1:8000
```

### Production Deployment
```bash
# Quick deploy script
./deploy.sh

# Docker deployment
docker-compose up -d

# Manual production setup
python manage.py migrate --settings=grupoMaster.settings_production
python manage.py collectstatic --noinput --settings=grupoMaster.settings_production
gunicorn --bind 0.0.0.0:8000 grupoMaster.wsgi:application
```

## Environment Variables

Key environment variables for production (see `env.example`):
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL configuration
- Email settings: `EMAIL_HOST`, `EMAIL_PORT`, etc.

## User Authentication

- Custom user model based on `AbstractUser`
- Users are associated with companies (`Empresa`)
- Login redirects to `/empresa-dashboard/`
- Master users have access to `/master-dashboard/`

## Key Business Logic

- **RAQS**: Registro de Qualificação de Soldador (Welder Qualification Record)
- **CQS**: Certificado de Qualificação de Soldador (Welder Qualification Certificate)
- Companies can create qualification requests for their welders
- Master users can approve/reject qualifications
- Various mechanical tests are tracked (tensile, bend, impact, etc.)

## File Uploads

- Media files stored in `media/` directory
- Company logos in `media/logos/`
- Static files served from `static/` (development) or `staticfiles/` (production)

## Logging

Production logging configured in `settings_production.py`:
- File logging to `logs/django.log`
- Console logging for real-time monitoring
- Verbose formatting with timestamps and module information