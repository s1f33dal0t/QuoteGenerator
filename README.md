# Quote Generator

Create professional quotes in minutes, not hours.

![Quote Generator Hero](docs/images/hero-overview.svg)

Quote Generator is a clean web app for small businesses that need to create quotes fast, export polished PDFs, and keep everything in one place.

## Why This Exists

Manual quotes in Word or spreadsheets are slow, error-prone, and hard to scale.

This project gives you a focused workflow:

- Add customer details
- Build quote line items
- Calculate totals and VAT automatically
- Export a professional PDF
- Track quote status over time
- Optionally generate line descriptions with AI

## Product Preview

### Dashboard

![Dashboard Placeholder](docs/images/screenshot-dashboard.svg)

### Create Quote Form

![Quote Form Placeholder](docs/images/screenshot-quote-form.svg)

### PDF Output

![PDF Placeholder](docs/images/screenshot-pdf.svg)

Note:
Replace these placeholder images with your real screenshots whenever you want. Keep the same filenames for zero README changes.

## Core Features

- Customer management (create, edit, delete)
- Quote builder with dynamic line items
- Automatic VAT and total calculations
- Quote status flow: draft, sent, accepted, rejected
- One-click PDF export
- Email send action from quote view
- Optional AI helper for service description text
- Health endpoint for quick runtime checks

## Tech Stack

- Backend: FastAPI
- Rendering: Jinja2 templates (server-rendered)
- ORM: SQLAlchemy
- Database: SQLite (demo) and PostgreSQL (supported)
- PDF engine: reportlab
- Optional AI: OpenAI API
- Deploy target: Render

## Quick Start (Local)

1. Create and activate virtual environment.
2. Install dependencies.
3. Copy env file.
4. Run app.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open:

- App: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health

## Environment Variables

Required for basic demo:

- `DATABASE_URL` (default: `sqlite:///./quote_generator.db`)
- `COMPANY_NAME`
- `COMPANY_EMAIL`

Optional:

- SMTP settings for email send
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `FROM_EMAIL`
- AI integration
  - `OPENAI_API_KEY`

## Database Modes

Demo mode:

- SQLite
- Example: `sqlite:///./quote_generator.db`

Production mode:

- PostgreSQL
- Example: `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME`

The app normalizes common Postgres URL formats automatically.

## Legacy Status Migration

If you have older Swedish status values in an existing SQLite database, run:

```bash
python scripts/migrate_legacy_statuses.py
```

Conversions:

- `utkast` -> `draft`
- `skickad` -> `sent`
- `accepterad` -> `accepted`
- `avvisad` -> `rejected`

When `DATABASE_URL` points to PostgreSQL, the migration script skips automatically.

## Deploy on Render (Demo)

This repository already includes a ready-to-use [render.yaml](render.yaml).

1. Push code to GitHub.
2. In Render, choose New + Blueprint.
3. Select this repository.
4. Render creates the web service from `render.yaml`.
5. Click deploy.

Start command used by Render:

```bash
python scripts/migrate_legacy_statuses.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For a pure demo, you can leave SMTP and OpenAI unset.

## API and Health

Health endpoint:

- `GET /health`

Example response:

```json
{
  "status": "ok",
  "database": "connected",
  "customers": 2,
  "quotes": 2
}
```

## Project Structure

```text
app/
  main.py
  config.py
  database.py
  models.py
  routes/
  templates/
  utils/
scripts/
  migrate_legacy_statuses.py
static/
  css/
render.yaml
run.py
```

## What To Replace Before Public Demo

- Company identity values in Render env vars
- Placeholder images in `docs/images/`
- SMTP credentials (if email sending should be active)
- OpenAI key (if AI text generation should be active)

## Roadmap Ideas

- Multi-user authentication
- Tax rate configuration per market
- Line-item templates
- Branded themes per customer segment
- Quote analytics and conversion metrics

## License

Use this project as a base for your own business workflow and customize freely.
