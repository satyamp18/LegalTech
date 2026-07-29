# LexVision AI – Contract Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.23+-orange.svg)](https://pymupdf.readthedocs.io/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-yellow.svg)](https://spacy.io/)

**LexVision AI** is a production-ready full-stack LegalTech enterprise application built for legal teams to automate contract intelligence, clause classification, legal risk scoring, metadata extraction, and legal audit report generation.

---

## 🌟 Key Features

- **Enterprise White Theme UI**: Clean, responsive, high-contrast SaaS interface with light gray backgrounds (`#f8fafc`), corporate deep blue (`#0f52ba`), soft shadow cards, sticky sidebar, and sticky header.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full platform & user authority, system settings, and Django Admin access.
  - **Lawyer**: Upload, analyze, review high-risk flags, re-run intelligence scans, export audit reports.
  - **Paralegal**: Document repository access, metadata review, and clause inspection.
- **PyMuPDF Document Engine**: Extracts high-speed PDF text, page layouts, block coordinates, and text metadata.
- **spaCy & Regex NLP Pipeline**:
  - Automatically extracts **Company Names**, **Contract Parties**, **Key Dates**, **Effective & Expiration Dates**, **Contract Duration**, **Governing Law**, and **Jurisdiction**.
  - Automatically classifies document text into **7 Core Legal Clause Categories**:
    1. Confidentiality
    2. Limitation of Liability
    3. Indemnification
    4. Termination
    5. Force Majeure
    6. Arbitration & Dispute Resolution
    7. Intellectual Property
- **Rule-Based Legal Risk Detection Engine**:
  - Scans contracts for high-risk legal liabilities (unlimited liability, unilateral termination for convenience, uncapped indemnification, perpetual non-disclosure, automatic renewal traps, foreign jurisdiction venues).
  - Calculates an overall **Risk Score (0–100)**, **Risk Level** (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and generates **Highlighted Sentences** and **AI Remediation Recommendations**.
- **Split-View Contract Workspace**:
  - **Left Panel**: Interactive embedded PDF viewer.
  - **Right Panel**: Extracted Metadata, Risk Score Gauge, Categorized Clauses, AI Recommendations, and Report Downloads.
- **Multi-Format Export Engine**: Download comprehensive contract audit reports in **PDF**, **CSV**, or **JSON** format.
- **REST API + JWT Authentication**: Clean DRF endpoints with SimpleJWT Bearer authentication, custom permission classes, and standard pagination.

---

## 🏗️ Project Architecture

```
LexVision/
├── apps/
│   ├── accounts/     # CustomUser model, JWT Auth, Role RBAC, User Profile, Settings
│   ├── documents/    # Document & Metadata models, PDF upload, list, split-view workspace
│   ├── analysis/     # PyMuPDF parser, spaCy NER, Regex service, Clause classifier, Risk Engine
│   ├── dashboard/    # Executive KPI metrics, Chart.js time-series, risk distribution stats
│   ├── reports/      # PDF (ReportLab), CSV, JSON audit report generation engine
│   └── common/       # Permissions, exception handlers, pagination, file validators
├── config/           # Django settings, root URLs, WSGI
├── static/           # LexVision CSS tokens, JS global search, PDF viewer scripts
├── templates/        # HTML5 / Bootstrap 5 responsive templates
├── Dockerfile        # Container build instructions
├── docker-compose.yml# PostgreSQL + Web container setup
├── requirements.txt  # Dependencies
└── manage.py
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.12+
- Git

### 2. Local Setup & Execution

```bash
# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy English model (Optional - built-in fallback included)
python -m spacy download en_core_web_sm

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Seed demo data (Creates Admin, Lawyer, Paralegal accounts & sample contracts)
python manage.py seed_data

# Start local server
python manage.py runserver 8000
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🔑 Demo Account Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@lexvision.ai` |
| **Lawyer** | `lawyer` | `lawyer123` | `lawyer@lexvision.ai` |
| **Paralegal** | `paralegal` | `paralegal123` | `paralegal@lexvision.ai` |

---

## 🐳 Docker Deployment

To run LexVision AI with Docker & PostgreSQL:

```bash
docker-compose up --build
```

Access the app at `http://localhost:8000`.

---

## 🛰️ REST API Documentation

- **POST** `/api/v1/auth/token/` - Obtain JWT Access & Refresh Token
- **POST** `/api/v1/auth/register/` - Register new user account
- **GET** `/api/v1/documents/` - List and search contracts
- **POST** `/api/v1/documents/` - Upload new PDF contract
- **GET** `/api/v1/documents/<id>/` - Retrieve contract details & analysis
- **GET** `/api/v1/analysis/<doc_id>/clauses/` - List categorized clauses
- **GET** `/api/v1/analysis/<doc_id>/risk/` - Get risk score and flags
- **GET** `/api/v1/documents/<doc_id>/report/pdf/` - Download PDF Report
- **GET** `/api/v1/documents/<doc_id>/report/csv/` - Download CSV Audit
- **GET** `/api/v1/documents/<doc_id>/report/json/` - Download JSON Payload
- **GET** `/api/v1/dashboard/stats/` - Executive Dashboard KPI metrics