# AI-driven Tender Scrutiny System for NLC India Limited (NLCIL)

An AI-driven automation platform developed to streamline and accelerate the industrial procurement tender evaluation process for NLC India Limited (NLCIL), Material Management Complex (MMC). This system decouples the **Vite + React Frontend** and **Flask REST API Backend** into a clean, modern, and production-ready architecture.

---

## Architecture Diagram

```
                 ┌────────────────────────────────┐
                 │       Browser (React UI)       │
                 └───────────────┬────────────────┘
                                 │
                                 │ REST API (JSON / Multipart)
                                 ▼
                 ┌────────────────────────────────┐
                 │       Flask Backend API        │
                 └───────────────┬────────────────┘
                                 │
      ┌──────────────────────────┼──────────────────────────┐
      ▼                          ▼                          ▼
┌───────────┐             ┌─────────────┐             ┌───────────┐
│    n8n    │             │  Selenium   │             │   Local   │
│ Workflow  │             │   + OCR     │             │  Storage  │
└─────┬─────┘             └──────┬──────┘             └─────┬─────┘
      │                          │                          │
      ▼                          ▼                          ▼
┌───────────┐             ┌─────────────┐             ┌───────────┐
│  Gemini   │             │    Udyam    │             │  Uploads  │
│  AI Engine│             │ Verification│             │ & Merges  │
└─────┬─────┘             └─────────────┘             └───────────┘
      │
      ▼
┌───────────┐
│  Google   │
│  Sheets   │
└───────────┘
```

---

## Project Structure

```text
project-root/
│
├── frontend/                     # React + Vite Application
│   ├── public/                   # Static assets (bg-3.webp, download.png, nlc.jpg)
│   ├── src/
│   │   ├── components/
│   │   │   └── layout/
│   │   │       ├── Header.jsx    # Logo and App Title
│   │   │       └── Header.css
│   │   ├── pages/
│   │   │   ├── Home/             # Welcome & Cards Page (Page 1)
│   │   │   ├── Merge/            # Upload & Merge Page (Page 2)
│   │   │   └── Evaluation/       # AI & Udyam Status Page (Page 3)
│   │   ├── services/
│   │   │   └── api.js            # Axios client mapping API routes
│   │   ├── App.jsx               # React Router configurations
│   │   ├── main.jsx              # Application render node
│   │   └── index.css             # Resets & Global background styles
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile                # Nginx production build Dockerfile
│
├── backend/                      # Flask REST API Application
│   ├── app/
│   │   ├── __init__.py           # Blueprints & CORS setups
│   │   ├── api/
│   │   │   └── routes/           # Blueprints mapping endpoints
│   │   │       ├── upload_routes.py
│   │   │       ├── merge_routes.py
│   │   │       ├── evaluation_routes.py
│   │   │       ├── workflow_routes.py
│   │   │       └── udyam_routes.py
│   │   ├── services/             # Core Business Logic Layer
│   │   │   ├── pdf_service.py    # Temporary uploads and deletes
│   │   │   ├── merge_service.py  # PyPDF2 merging service
│   │   │   ├── workflow_service.py # n8n integration service
│   │   │   └── udyam_service.py  # Selenium captcha bypass and scraping
│   │   └── core/
│   │       ├── config.py         # Config loader matching .env
│   │       └── logging.py        # Stream logging configuration
│   ├── run.py                    # API launcher script
│   ├── requirements.txt          # Python packages list
│   └── Dockerfile                # Selenium + OCR package build Dockerfile
│
├── scripts/                      # Developer automation scripts
│   ├── start-dev.bat             # Runs backend + frontend in double CMD
│   └── start-dev.ps1             # Runs backend + frontend in PowerShell
│
├── .env.example                  # Environmental configurations blueprint
├── docker-compose.yml            # Docker configurations orchestrator
└── README.md
```

---

## API Documentation

The Flask Backend exposes clean, stateless REST API endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/files/upload` | Upload multiple PDF files |
| `GET` | `/api/files` | Retrieve list of uploaded working files |
| `DELETE`| `/api/files/<filename>`| Delete specific uploaded file |
| `GET` | `/api/files/<filename>/download` | Download specific uploaded file |
| `POST` | `/api/files/clear` | Clear all working files |
| `POST` | `/api/merge` | Merge uploaded files |
| `GET` | `/api/merge/files` | Get list of files available for merge |
| `POST` | `/api/workflow/start` | Trigger AI evaluation workflow via n8n |
| `GET` | `/api/workflow/status/<id>` | Poll status of AI evaluation workflow |
| `POST` | `/api/udyam/verify` | Trigger Udyam Selenium scraping/webhook |
| `GET` | `/api/udyam/status/<id>`| Poll status of Udyam Verification process |
| `GET` | `/api/health` | Service health status check |

---

## Tech Stack

- **Frontend**: React, Vite, JavaScript, React Router, Axios, Vanilla CSS (Page-Scoped Wrapper isolation).
- **Backend**: Flask, Flask-CORS, PyPDF2, Requests, Pandas, Openpyxl, OpenCV, Tesseract OCR, Selenium, webdriver-manager.
- **Integrations**: n8n workflows, Google Gemini API, Google Sheets API.

---

## Environment Variables

Configure the system by creating a `.env` file at the root workspace (copied from `.env.example`):

```env
# Flask Server Config
SECRET_KEY=nlc-tender-scrutiny-secret-key-2025
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# n8n Integration Webhook Settings
N8N_BASE_URL=http://localhost:5678
N8N_EVALUATION_WEBHOOK=/webhook/93f97adb-c532-44d9-9942-da74472c8cb6
N8N_UDYAM_WEBHOOK=/webhook/YOUR_UDYAM_WEBHOOK_ID

# Google Sheets Configuration
GOOGLE_SHEETS_ID=1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0/edit?usp=sharing

# Google Gemini API Config
GEMINI_API_KEY=your-gemini-api-key-here

# Tesseract OCR & Selenium ChromeDriver Configurations
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
CHROME_DRIVER_PATH=

# Udyam Verification Excel Input/Output Paths
UDYAM_INPUT_EXCEL=C:/Users/syles/Documents/NLC/N8N.xlsx
UDYAM_OUTPUT_EXCEL=C:/Users/syles/Documents/NLC/scraped_output.xlsx
UDYAM_COLUMN=udyam registration
MAX_CAPTCHA_ATTEMPTS=50
```

---

## Setup & Running Guide

### 1. Prerequisites

- **Python 3.10+**: Ensure Python is in your system PATH.
- **Node.js 18+**: For compiling Vite React.
- **Tesseract OCR**: Download, install, and specify path in `.env` (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).

### 2. Quickstart Developer Run (Local)

Simply double click the startup script:

- **Windows Batch**: Run `scripts/start-dev.bat`
- **PowerShell**: Run `scripts/start-dev.ps1`

Alternatively, start them manually:

**Backend Setup:**
```bash
cd backend
python -m venv venv
# Windows activate
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

### 3. Docker Compose Orchestration (Containerized)

To build and run the backend and frontend in containerized environments:

```bash
docker-compose up --build
```

- **Frontend UI** is exposed at: `http://localhost:80`
- **Backend API** is exposed at: `http://localhost:5000`

---

## Integration Details

### Gemini and n8n Setup
- The Start Scrutiny evaluation sends the file collection to the local backend.
- The backend delegates this payload to the n8n Workflow Webhook.
- n8n segments the document text, queries the Google Gemini API to extract key clauses (EMD, PQR, MSME), saves logs, and updates the Google Sheets sheet before sending a success status code back to the React UI.

### Udyam Captcha Bypass & Scrape
- When Udyam Verification is clicked, the React UI submits a request to the backend.
- The Selenium scraper boots up chrome driver, goes to Udyam print/verify page, crops out the captcha image.
- OpenCV enhances the image (grayscale, thresh, morphological closing, interpolation), and Tesseract OCR bypasses the captcha automatically.
- Upon login, the scraper extracts enterprise data, classifications, and dates, then updates the output Excel sheet.

---

## Troubleshooting

- **CORS Errors**: Confirm that `CORS_ORIGINS` in `.env` contains the port Vite is running on (`http://localhost:5173`).
- **OCR Tesseract Path Error**: Check that the path to `tesseract.exe` is set correctly in `.env` using forward slashes (e.g. `C:/Program Files/Tesseract-OCR/tesseract.exe`).
- **Chrome Driver Incompatibility**: `webdriver-manager` installs chromedriver automatically. If it fails, specify a manual path under `CHROME_DRIVER_PATH`.
