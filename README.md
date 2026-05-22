Management System (Flask)

Task & Expense Management System - backend (Flask) and simple frontend.

Run locally:

1. Create `.env` from `.env.example` and set DB settings
2. Install requirements: `python -m pip install -r requirements.txt`
3. Start backend: `python backend/app.py`
4. Start frontend (optional): `cd frontend && python -m http.server 8000`

Docker setup:

1. Build and start all services:

   ```bash
   docker compose up --build
   ```

2. Open the frontend in your browser:

   ```bash
   http://localhost:8000/pages/users.html
   ```

3. The backend API will be available at:

   ```bash
   http://localhost:5000/api/health
   ```

Notes:
- The compose file includes `db` (SQL Server), `backend`, and `frontend`.
- Update `docker-compose.yml` if you want a stronger `SA_PASSWORD` or different DB values.
- If you already have SQL Server elsewhere, you can skip the `db` service and point `DB_SERVER` to your server.
