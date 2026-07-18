# LegalTech Backend

Enterprise Legal Document Management and Risk Analysis API backend built with Django and Django REST Framework.

## Project Structure

This project follows an enterprise-standard modular directory structure where all custom applications reside under the `apps/` directory:

```text
LegalTech/
├── .env                  # Local environment configuration (ignored)
├── .env.example          # Template for environment configuration
├── .gitignore            # Git ignore patterns
├── manage.py             # Django management CLI
├── README.md             # Developer documentation
├── requirements.txt      # Python dependencies
├── logs/                 # Application logs (ignored)
├── legaltech_backend/    # Core Django settings & entrypoints
│   ├── settings.py       # Base settings (CORS, REST, logs, database)
│   ├── urls.py           # Core URL routing
│   └── ...
└── apps/                 # Custom Django apps folder
    ├── accounts/         # User accounts and authentication module
    ├── contracts/        # Contracts management module
    ├── parser/           # Document parsing engine
    └── risk_engine/      # Risk analysis engine
```

---

## Local Setup

### 1. Prerequisites
- Python 3.12+
- PostgreSQL database

### 2. Environment Setup

Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

Install requirements:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory based on `.env.example`:
```bash
cp .env.example .env
```
Update the `.env` file with your local database credentials and key configurations.

### 4. Database Setup & Migrations

Ensure PostgreSQL is running and the database specified in your `.env` exists. Then apply database migrations:
```bash
python manage.py migrate
```

---

## Running the Server

Start the Django development server:
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

---

## API Documentation

The project uses `drf-spectacular` for OpenAPI 3.0 schema generation and Swagger UI.

Once the development server is running, you can access documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)
- **Raw OpenAPI Schema (JSON)**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
