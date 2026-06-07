# Warehouse Product Verifier

A full-stack warehouse management system for bulk product data ingestion, on-the-floor product verification with AI-powered label scanning, and compliance reporting.

A production-grade warehouse operations system built for supply chain inventory management and compliance.

---

## Application Walkthrough

<table>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/login_page.png" alt="Login Page" width="100%"/>
      <br/><br/>
      <b>Step 1 — Login</b>
      <br/>JWT-based authentication. Admin redirects to the dashboard; operators redirect directly to the Verify page.
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/upload_data_page.png" alt="Upload CSV" width="100%"/>
      <br/><br/>
      <b>Step 2 — Bulk CSV Upload</b>
      <br/>Admin drags a CSV file. Celery processes up to 1 crore rows in the background with a live progress bar and row counter.
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/product_data_page.png" alt="Product Data" width="100%"/>
      <br/><br/>
      <b>Step 3 — Browse & Search Products</b>
      <br/>Paginated view of all uploaded products. Search by WID or EAN for instant lookup across the full dataset.
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/product_verification_1.png" alt="Verify Step 1" width="100%"/>
      <br/><br/>
      <b>Step 4 — Verify Product: WID Lookup</b>
      <br/>Operator or admin enters a WID. The system instantly shows EAN, manufacturing date, expiry date, and expiry status.
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/product_verification_2.png" alt="Verify Step 2" width="100%"/>
      <br/><br/>
      <b>Step 5 — Verify Product: Label Image Upload</b>
      <br/>Upload or capture a photo of the physical product label. Supports drag-and-drop and mobile camera capture.
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/product_verification_3.png" alt="Verify Step 3 — AI Result" width="100%"/>
      <br/><br/>
      <b>Step 6 — AI Extraction Result</b>
      <br/>Azure OpenAI GPT-4o reads the label and extracts dates. Result (MATCH / MISMATCH / ERROR) is shown and saved to the verification log automatically.
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/verification_reports.png" alt="Verification Reports" width="100%"/>
      <br/><br/>
      <b>Step 7 — Compliance Reports</b>
      <br/>QA Manager selects a date range to view all verification events. Filterable by date, downloadable as CSV for audit records.
    </td>
    <td align="center" width="50%">
      <img src="docs/screenshots/user_management.png" alt="User Management" width="100%"/>
      <br/><br/>
      <b>Step 8 — User Management</b>
      <br/>Admin views all users with role and status badges. Role-based access ensures admins upload/report while operators only verify.
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="docs/screenshots/user_management_2.png" alt="Create User" width="100%"/>
      <br/><br/>
      <b>Step 9 — Create New User</b>
      <br/>Admin creates users with assigned roles (admin or operator). Passwords are bcrypt-hashed; tokens expire after 8 hours aligned to a warehouse shift.
    </td>
    <td align="center" width="50%">
      <!-- Reserved for future screenshot -->
    </td>
  </tr>
</table>

---

## Features

### Core (Phase A1)
- **Bulk CSV Ingestion** — Upload CSVs with millions of rows. Processing runs in the background via Celery; the UI shows live progress with rows processed, total rows, and percentage.
- **Product Browse & Search** — Paginated table of all products with search by WID or EAN.
- **On-the-Floor Validation** — Warehouse operators enter a WID to instantly see EAN, manufacturing date, and expiry date. Every lookup is logged automatically.
- **Verification Reports** — QA managers select a date range and generate a full audit of all verification events. Export to CSV included.

### AI Integration (Phase A2)
- **GPT-4o Vision Extraction** — On the Verify page, upload or capture a photo of the product label. Azure OpenAI GPT-4o extracts manufacturing and expiry dates from the image and compares them against database values. Results (MATCH / MISMATCH / ERROR) are saved to the verification log.

### Auth & RBAC (Phase A3)
- **JWT Authentication** — 8-hour tokens aligned with a warehouse shift.
- **Role-based Access Control** — Two roles: `admin` and `operator`.
  - Admin: CSV upload, reports, user management, product browse, verify.
  - Operator: Verify product only (`/validate`).

---

## Architecture

> Click the diagram to view full size.

[![Architecture Diagram](docs/screenshots/architecture.png)](docs/screenshots/architecture.png)

**Key design decisions:**

| Decision | Rationale |
|---|---|
| PostgreSQL `COPY` + staging table | 10–100× faster than row-by-row INSERT for bulk ingestion |
| Celery + Redis | Async task queue — server never blocks, upload survives restarts |
| `ON CONFLICT DO UPDATE` on WID | Guarantees idempotent uploads — re-uploading the same file is safe |
| B-tree index on `wid`, `verified_at` | Sub-millisecond WID lookups and fast date-range report queries |
| GPT-4o zero-shot vision | Handles any label format without fine-tuning |
| JWT (HS256), 8-hour expiry | Aligned with warehouse shift length |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI 0.115 |
| Task Queue | Celery 5.4 + Redis 7 |
| Database | PostgreSQL 16, SQLAlchemy 2.0 (async), Alembic |
| AI | Azure OpenAI GPT-4o (vision) |
| Frontend | React 18, Vite 4, Ant Design 5 |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Deployment | Azure Container Apps, Azure Static Web Apps, Azure Container Registry |

---

## Prerequisites

- Python 3.11+
- Node.js 16+ and npm
- PostgreSQL 16 (local install)
- Docker (for Redis container)
- Azure OpenAI resource with GPT-4o deployment

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/prakharjadaun/warehouse-product-verifier.git
cd warehouse-product-verifier
```

### 2. Configure environment variables

```bash
cp .env.example backend/.env
```

Edit `backend/.env` with your values:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/wms_dev
REDIS_URL=redis://localhost:6379/0
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_LLM_DEPLOYMENT=gpt-4o
AZURE_LLM_API_VERSION=2025-01-01-preview
SECRET_KEY=your-random-secret-key
ALLOWED_ORIGINS=http://localhost:5173
```

### 3. Create PostgreSQL databases

```sql
CREATE DATABASE wms_dev;
CREATE DATABASE wms_test;
```

### 4. Start Redis via Docker

```bash
docker run -d --name wms-redis -p 6379:6379 -v wms-redis-data:/data redis:7-alpine redis-server --appendonly yes
```

### 5. Install backend dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Seed the first admin user

```bash
python seed_admin.py
# Creates: admin@warehouse.com / admin123
```

### 8. Install frontend dependencies

```bash
cd ../frontend
npm install
```

---

## Running Locally

### Option A — One-click startup (Windows)

Double-click `start.bat` from the repo root. It opens three terminal windows:
- FastAPI backend on `http://localhost:8000`
- Celery worker
- React frontend on `http://localhost:5173`

### Option B — Manual (cross-platform)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Celery worker:**
```bash
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` and login with `admin@warehouse.com` / `admin123`.

---

## API Reference

Full interactive docs available at `http://localhost:8000/docs` when the backend is running.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | Get JWT token |
| POST | `/auth/users` | Admin | Create user |
| GET | `/auth/users` | Admin | List all users |
| POST | `/uploads/csv` | Admin | Upload CSV file (async) |
| GET | `/uploads/{job_id}/status` | Admin | Poll upload job progress |
| GET | `/uploads` | Admin | Upload history |
| GET | `/products` | Any | Browse/search products |
| GET | `/products/{wid}` | Any | Get product by WID |
| POST | `/verifications` | Any | Log a verification event |
| POST | `/verifications/ai-extract` | Any | Upload image + run GPT-4o extraction |
| GET | `/reports/verifications` | Admin | Date-range verification report |
| GET | `/health` | Public | Health check |

---

## Running Tests

```bash
cd backend
pytest tests/ -v --ignore=tests/test_ingest_service.py
```

Expected: **25 tests passing** across auth, uploads, validations, reports, and AI service modules.

For the ingest service integration test (requires wms_test DB):
```bash
pytest tests/test_ingest_service.py -v
```

---

## Database Schema

```
products           — WID (PK), EAN, manufacturing_date, expiry_date
upload_jobs        — job_id (PK), filename, status, total_rows, processed_rows
verification_logs  — id (PK), wid, operator_id, image_path, db dates, ai dates, match_status
users              — id (PK), email, hashed_password, role (admin|operator)
```

---

## Deployment (Azure)

### Infrastructure required

| Resource | Service |
|---|---|
| Container Apps Environment | Hosts `api` and `worker` containers |
| Azure Container Registry | Docker image store |
| Azure Database for PostgreSQL Flexible Server | Production database |
| Azure Cache for Redis | Celery broker |
| Azure Static Web Apps | React frontend |
| Azure OpenAI | GPT-4o vision endpoint |

### CI/CD Pipeline

Push to `main` triggers GitHub Actions:
1. Run pytest test suite
2. Build Docker image
3. Push to Azure Container Registry
4. Deploy `api` Container App (FastAPI)
5. Deploy `worker` Container App (Celery)

Required GitHub secrets: `ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`, `AZURE_CREDENTIALS`, `AZURE_RESOURCE_GROUP`.

### Build and run with Docker

```bash
# Build image
docker build -t wms-backend ./backend

# Run API
docker run -p 8000:8000 --env-file backend/.env wms-backend

# Run Celery worker
docker run --env-file backend/.env wms-backend worker
```

---

## How to Use

### 1. Upload product data (Admin)
- Login as admin → **Upload CSV**
- Drag and drop the CSV file
- Watch live progress — rows processed update every few seconds
- View upload history below the upload area

### 2. Browse and search products (Admin)
- Go to **Products** in sidebar
- Click **Browse All** to see all products
- Search by WID or EAN for instant lookup

### 3. Verify a product on the warehouse floor (Admin/Operator)
- Go to **Verify Product** (admin) or `http://localhost:5173/validate` (operator)
- Enter WID — product details shown instantly
- Upload or capture a photo of the physical label
- Click **Run AI Verification** — GPT-4o extracts dates and shows MATCH or MISMATCH
- Result is saved automatically to the verification log

### 4. Generate compliance report (Admin)
- Go to **Reports**
- Select start and end date
- Click **Generate Report**
- View all verification events with AI match status
- Download as CSV for compliance records

---

## Project Structure

```
warehouse-product-verifier/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── config.py            # Environment config (pydantic-settings)
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── celery_app.py        # Celery + Redis configuration
│   │   ├── dependencies.py      # JWT auth + RBAC dependencies
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── routers/             # FastAPI route handlers
│   │   ├── services/            # Business logic (ingest, AI, auth)
│   │   └── tasks/               # Celery task definitions
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # pytest test suite (25 tests)
│   ├── seed_admin.py            # First admin user setup script
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/admin/         # Upload, Products, Verify, Reports, Users
│       ├── pages/operator/      # Validate (mobile-optimized)
│       ├── context/AuthContext  # JWT state management
│       ├── components/          # PrivateRoute
│       └── api/client.js        # Axios with auth interceptors
├── start.bat                    # One-click local startup (Windows)
├── docker-compose.yml           # Full local stack with Docker
└── .env.example                 # Environment variable template
```
