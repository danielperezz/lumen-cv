# Server

## Local Postgres

Start a local Postgres database that matches the default `DATABASE_URL` in `server/config.py`:

```bash
docker run --name lumen-cv-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=lumen_cv \
  -p 5432:5432 \
  -d postgres:16
```

If the container already exists, start it again with:

```bash
docker start lumen-cv-postgres
```

The default local database URL is:

```text
postgresql+psycopg2://postgres:postgres@localhost:5432/lumen_cv
```

You can override it with a root `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/lumen_cv
```

## Local API

Run the FastAPI server locally on port 8000:

```bash
uv run uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

The API root will be available at:

```text
http://localhost:8000/
```
