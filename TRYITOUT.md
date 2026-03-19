# Try It Out — Quick Start Guide

Two ways to try the Prison Book Project app: run it locally with Docker, or deploy a free instance on Railway.

---

## Option 1: Run Locally with Docker (Mac)

### Prerequisites

Install **Docker Desktop** for Mac: https://www.docker.com/products/docker-desktop/

That's it — Docker Desktop includes everything you need.

### Steps

1. Open **Terminal** (search "Terminal" in Spotlight)

2. Navigate to this project folder:
   ```
   cd path/to/prisonbookproject
   ```

3. Start everything with one command:
   ```
   docker compose up --build
   ```
   The first run will take a few minutes to build. Subsequent starts are fast.

4. Open your browser to: **http://localhost:8000/admin/**

5. Log in with:
   - **Username:** `admin`
   - **Password:** `admin`

6. To stop: press `Ctrl+C` in the terminal, or run:
   ```
   docker compose down
   ```

### Notes

- Your data is saved between restarts (stored in a Docker volume)
- To completely reset and start fresh:
  ```
  docker compose down -v
  docker compose up --build
  ```

---

## Option 2: Deploy to Railway (Free Hosted Instance)

Railway gives you a hosted instance with a public URL — no installation needed on your computer.

### Steps

1. Create a free account at https://railway.com

2. From the Railway dashboard, click **"New Project"** → **"Deploy from GitHub Repo"**

3. Connect your GitHub account and select this repository

4. Railway will detect the Dockerfile automatically. Before deploying, add a **PostgreSQL database**:
   - Click **"New"** → **"Database"** → **"PostgreSQL"**

5. In the web service settings, add these **environment variables** (Settings → Variables):
   ```
   DATABASE_URL        → (click "Add Reference" and select the PostgreSQL connection string)
   SECRET_KEY          → any-random-string-here
   ALLOWED_HOSTS       → *
   CORS_WHITELIST      → https://your-app-name.up.railway.app
   CSRF_TRUSTED_ORIGINS → https://your-app-name.up.railway.app
   ENV_NAME            → production
   DEBUG               → False
   DJANGO_SUPERUSER_USERNAME → admin
   DJANGO_SUPERUSER_PASSWORD → pick-a-password
   DJANGO_SUPERUSER_EMAIL    → your@email.com
   ```

6. Deploy! Railway will build and start the app. Click the generated URL to access it.

7. Go to `https://your-app-url.up.railway.app/admin/` and log in with your chosen credentials.

### Notes

- Railway's free tier includes 500 hours/month of runtime and a PostgreSQL database
- The `railway.toml` in this repo configures the build and deploy settings automatically
- To redeploy after changes, just push to the connected GitHub branch
