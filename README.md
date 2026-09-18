# LexVision – AI-Powered Legal Contract Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![Gemini API](https://img.shields.io/badge/Google%20Gemini-GenAI-blueviolet.svg)](https://ai.google.dev/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.23+-orange.svg)](https://pymupdf.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

**LexVision** is a clean, practical LegalTech platform designed to help legal professionals and businesses quickly upload PDF contracts, extract raw text, classify legal clauses, score legal risk exposure, and generate Generative AI executive summaries using the **Google Gemini API**.

---

## 📌 Problem Statement

Legal teams and business professionals frequently review lengthy legal contracts (NDAs, Service Agreements, Vendor Contracts). Manual contract review is:
- **Time-consuming**: Reading 30-50 page contracts line by line takes hours.
- **Error-prone**: Critical risk clauses like unlimited financial liability or automatic renewal traps can easily be overlooked.
- **Opaque for non-lawyers**: Complex legalese makes it difficult for business stakeholders to quickly understand contract obligations.

---

## 💡 Solution

**LexVision** automates contract analysis through a simple, effective pipeline:
1. **PDF Text Extraction & Cleaning**: Parses PDF documents into clean, structured text using PyMuPDF.
2. **Rule-Based Algorithmic Risk Identification**: Uses fast dictionary lookups and regular expressions to flag high-risk legal terms (unlimited liability, immediate unilateral termination, uncapped indemnity).
3. **Generative AI Integration**: Sends cleaned contract text to **Google Gemini API** to generate concise plain-language executive summaries and clause explanations.
4. **Interactive Dashboard & Audit Reports**: Displays contract risk gauges, extracted metadata, categorized clauses, and downloadable PDF/CSV/JSON audit reports.

---

## ✨ Features

- **User Authentication & RBAC**: Secure Django session & JWT authentication with support for Admin, Lawyer, and Paralegal roles.
- **PDF Upload & Processing**: Fast text extraction using PyMuPDF (`fitz`).
- **Text Normalization**: Cleans whitespace, strips control characters, and splits text into logical sections.
- **Google Gemini Integration**: 
  - Generates 3-4 sentence contract executive summaries.
  - Translates complex legal clauses into plain language.
  - Provides AI remediation guidance for flagged risks.
- **Rule-Based Risk Scoring (0–100)**: Evaluates contracts for high, medium, and low severity legal risks.
- **Categorized Clause Extraction**: Identifies Confidentiality, Limitation of Liability, Indemnification, Termination, Force Majeure, and Governing Law clauses.
- **Audit Report Exports**: Download reports in PDF, CSV, or JSON format.
- **Docker Support & Developer Makefile**: Simple single-command container startup and test execution.

---

## 🛠️ Technology Stack

- **Backend Language**: Python 3.12
- **Web Framework**: Django 5.0+, Django REST Framework (DRF)
- **Database**: SQLite (Development) / PostgreSQL (Docker/Production)
- **Generative AI**: Google Gemini API (`gemini-2.5-flash`)
- **PDF Engine**: PyMuPDF (`fitz`)
- **NLP & Regex**: spaCy (`en_core_web_sm`), Python `re` module
- **Containerization**: Docker & Docker Compose
- **Testing**: Python `unittest` / Django `TestCase` with `unittest.mock`

---

## 🏗️ Architecture

```text
                               +-----------------------------+
                               |     User Interface (Web)    |
                               +--------------+--------------+
                                              |
                                              v
                               +--------------+--------------+
                               |     Django Web & REST API   |
                               +--------------+--------------+
                                              |
               +------------------------------+------------------------------+
               |                              |                              |
               v                              v                              v
+--------------+--------------+ +-------------+---------------+ +------------+--------------+
|  PDF & Text Preprocessing   | | Rule-Based Risk Engine (DSA) | |  Google Gemini AI Service    |
| (PyMuPDF / Clean Pipelines) | | (Dictionaries & O(N) Regex) | |   (Contract Summaries)     |
+--------------+--------------+ +-------------+---------------+ +------------+--------------+
               |                              |                              |
               +------------------------------+------------------------------+
                                              |
                                              v
                               +--------------+--------------+
                               |     Database (PostgreSQL)   |
                               +-----------------------------+
```

---

## 🧠 Algorithmic Thinking & Data Structures

To keep processing efficient without over-engineering:
- **Dictionary Lookups (Hash Maps)**: Legal risk categories are mapped in Python dictionaries for O(1) keyword indexing:
  ```python
  RISK_KEYWORDS = {
      "unlimited_liability": ["unlimited liability", "no limitation of liability"],
      "unilateral_termination": ["terminate at any time without cause"],
      "broad_indemnification": ["indemnify defend and hold harmless"]
  }
  ```
- **Linear Text Scanning**: Text is scanned in a single pass O(N) using regular expressions before sending relevant snippets to the Gemini API, minimizing unnecessary API token consumption.
- **Text Normalization**: Regex-based whitespace stripping and section splitting chunk long documents into structured sections.

---

## 🤖 Google Gemini AI Integration

The Gemini integration uses environment variables and clean exception handling:

```text
User Uploads PDF -> Extract & Clean Text -> Prompt Construction -> Gemini API Call -> AI Summary Returned -> Displayed in UI
```

### Environment Variable Setup:
Set `GEMINI_API_KEY` in your `.env` file:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key
```
If `GEMINI_API_KEY` is not set or network fails, LexVision provides a friendly fallback message without crashing the application.

---

## 🛠️ Developer Commands (Makefile)

LexVision includes a beginner-friendly `Makefile`:

| Command | Description |
|---|---|
| `make install` | Install Python dependencies & spaCy model |
| `make migrate` | Apply database migrations |
| `make run` | Start Django dev server at `http://127.0.0.1:8000` |
| `make test` | Run automated unit tests |
| `make docker-up` | Build and start Docker containerized stack |
| `make docker-down` | Stop Docker containers |

---

## 🐳 Docker Setup

To run LexVision in a containerized environment with PostgreSQL:

```bash
# Build and launch application
docker compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Testing

LexVision includes unit tests that mock external API calls so tests run fast and offline:

```bash
# Run unit test suite
python manage.py test apps.analysis apps.documents apps.accounts
```

All 8 tests pass cleanly out-of-the-box.

---

## 🔑 Demo Account Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@lexvision.ai` |
| **Lawyer** | `lawyer` | `lawyer123` | `lawyer@lexvision.ai` |
| **Paralegal** | `paralegal` | `paralegal123` | `paralegal@lexvision.ai` |

---

## 📄 License
Developed for educational, portfolio, and interview demonstration purposes.