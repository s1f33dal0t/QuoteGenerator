# Quote Generator (Demo)

A small FastAPI app for creating and sending professional quotes.

## Features

- Customer list and customer management
- Quote creation form with line items
- Automatic PDF generation
- Quote history and status updates
- Email action: send quote to customer
- Optional AI helper for generating line-item description text

## Tech Stack

- Backend: FastAPI
- Templates: Jinja2 (server-rendered)
- Database: SQLite (SQLAlchemy)
- PDF: reportlab
- Optional AI: OpenAI API

## Database Modes

- Local/demo: SQLite with `quote_generator.db`
- Public production: PostgreSQL (recommended)

The app supports both with `DATABASE_URL`.

Examples:

- SQLite: `sqlite:///./quote_generator.db`
- PostgreSQL: `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME`

## Local Run

1. Create and activate a virtual environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Copy environment file and update values:

   cp .env.example .env

4. Start the app:

   python run.py

5. Open:

   http://127.0.0.1:8000

6. Optional health check:

   http://127.0.0.1:8000/health

The default local SQLite file is:

   quote_generator.db

## Legacy Data Migration

If you have an older database with Swedish quote statuses, run:

   python scripts/migrate_legacy_statuses.py

This converts old values to the current English statuses:

- utkast -> draft
- skickad -> sent
- accepterad -> accepted
- avvisad -> rejected

## Deploy on Render (Demo)

This repo includes a render.yaml blueprint.

1. Push this folder to GitHub.
2. In Render, create a new Blueprint and select the repo.
3. Render reads render.yaml and creates the web service + disk.
4. Set real SMTP and OPENAI_API_KEY values in Render Environment.
5. Deploy.

The demo stores SQLite data on a Render disk mounted at /var/data.
The Render start command runs the legacy status migration automatically before the app boots.

## Deploy on Render (Production with Postgres)

1. Create a PostgreSQL database in Render.
2. Set `DATABASE_URL` in the web service environment to the internal DB URL from Render.
3. Remove the disk block if you do not need SQLite persistence.
4. Keep the same start command.

The migration script auto-skips when `DATABASE_URL` is not SQLite.

## Health Check

The app exposes a small health endpoint:

   /health

It returns app status, database connectivity, and simple row counts.
