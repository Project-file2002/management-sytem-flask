# Docker Setup Instructions

Yeh file aapko guide karegi ki is project ko kisi dusre PC par kaise chalana hai, bina errors ke.
Sabhi Docker images already aapke Docker Hub account (`creatorhoon`) par push ho chuki hain.

## 1. Prerequisites (Pehli Baar Setup)
Dusre PC par project chalane se pehle yeh zaroori hai:
1. **Docker Desktop** install karein: [Download Link](https://www.docker.com/products/docker-desktop/)
2. Installation ke baad apna PC **Restart** zaroor karein.
3. Start menu se Docker Desktop open karein aur ensure karein ki bottom-left corner mein "Engine Running" (green icon) show ho raha ho.

---

## 2. Dusre PC Par Project Chalana

Kyunki humne images ko Docker Hub par push kar diya hai, aapko source code ko wapas build karne ki zaroorat nahi hai.

### Step 1: Project Files Copy Karein
Aapko pura project folder nahi chahiye, sirf niche di gayi 2 files chahiye (ek naye folder mein rakhein):
1. `docker-compose.yml`
2. `.env` file (Kyunki yeh git pe nahi hoti, ise `.env.example` se copy karke banayein)

### Step 2: `docker-compose.yml` File Update Karein
Apne naye PC par `docker-compose.yml` file open karein aur `image` ka naam update karein taaki wo aapke Docker Hub account se images download kare. Niche diye gaye changes karein:

**1. Database (db) service:**
```yaml
  db:
    image: creatorhoon/tems:db
    # baki sab (environment, ports, volumes) same rakhein
```

**2. Backend (backend) service:**
```yaml
  backend:
    image: creatorhoon/tems:backend
    # 'build: context: .' wali lines ko HATA dein
    # baki sab same rakhein
```

**3. Frontend (frontend) service:**
```yaml
  frontend:
    image: creatorhoon/tems:frontend
    # 'build: context: .' wali lines ko HATA dein
    # baki sab same rakhein
```

### Step 3: Run Karein
Terminal ya Command Prompt us folder mein open karein jahan aapne `docker-compose.yml` rakhi hai aur run karein:

```bash
docker compose up
```

- Pehli baar mein yeh internet se images download karega (isme thoda waqt lag sakta hai).
- Ek baar download hone ke baad aapka database, backend, aur frontend teeno start ho jayenge!

---

## 3. Application Use Karein

Jab terminal mein koi nayi error na aaye, tab apne browser mein yeh URLs open karein:

- **Frontend (Website):** http://localhost:8000
- **Backend (API Health Check):** http://localhost:5000/api/health

### Default Login Credentials
Database automatic initialize hone ke baad ek admin account create kar deta hai:
- **Email:** `admin@system.com`
- **Password:** `Admin@123`

---

## Important Notes:
- **Data Save Kahan Hota Hai?** Database ka data ek local volume (`db_data`) mein save hota hai. Image update karne se data delete nahi hota, lekin PC change karne par naya database banega.
- **Stop Kaise Karein?** Terminal mein `Ctrl + C` press karein ya `docker compose down` run karein.
