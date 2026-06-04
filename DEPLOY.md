# Deploying to Render (free)

This API is configured to deploy on [Render](https://render.com) using the
free **Web Service** tier. The config lives in [`render.yaml`](render.yaml).

## What's included

| File              | Purpose                                                        |
|-------------------|----------------------------------------------------------------|
| `render.yaml`     | Render Blueprint — defines the free web service.               |
| `Procfile`        | Start command, also works on other hosts (Railway, Heroku).    |
| `.python-version` | Pins Python to 3.12.7 for a reproducible build.                |
| `requirements.txt`| Dependencies installed during the build.                       |

The service runs:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Render provides the `$PORT` automatically — do not hard-code a port.

## Steps

### 1. Push this project to GitHub

If it isn't on GitHub yet:

```powershell
git init                      # only if not already a repo
git add .
git commit -m "Khmer public holidays API"
# create an empty repo on github.com first, then:
git remote add origin https://github.com/<your-username>/khmer-public-holidays.git
git branch -M main
git push -u origin main
```

### 2. Create the service on Render

1. Sign up / log in at https://render.com (free, GitHub login works).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub account and pick this repository.
4. Render reads `render.yaml` and shows the `khmer-public-holidays-api` service
   on the **Free** plan. Click **Apply**.
5. Wait for the build + deploy (a few minutes the first time).

> Alternatively: **New +** → **Web Service**, pick the repo, and Render
> auto-detects Python. Set the start command to the one above if asked.

### 3. Use your live API

Render gives you a URL like:

```
https://khmer-public-holidays-api.onrender.com
```

- API docs: `https://<your-app>.onrender.com/docs`
- Holidays: `https://<your-app>.onrender.com/holidays`

## Free-tier things to know

- **Cold starts:** the free service sleeps after ~15 minutes of inactivity.
  The next request wakes it and may take ~30–60 seconds. This is normal.
- **Ephemeral disk:** the filesystem resets on every restart/redeploy. Reads of
  the seeded holidays always work, but any holidays you **create / update /
  delete** at runtime are **not** kept permanently. For a class demo this is
  fine; for durable writes you would switch `storage.py` to a hosted database
  (e.g. Render's free PostgreSQL, or Supabase).
- **Auto-deploy:** `autoDeploy: true` means every push to `main` redeploys.
