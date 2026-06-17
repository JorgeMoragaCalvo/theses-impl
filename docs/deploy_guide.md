# Guide to deploying on DigitalOcean (DO)

## Step 1 — Create a Droplet
In DO dashboard → Droplets → Create Droplet:
- Image: Ubuntu 24.04 LTS
- Plan: Basic → Regular → $12/mo (2GB RAM, 1 vCPU)
- Region: nyc1
- **Authentication**. Add your SSH key:
  - Open a PowerShell (PS) terminal in your local and enter: `ssh-keygen`
  - If you want to store your key in a password-protected file, create a new file if not press enter.
  - Create any password.
  - To copy the SSH key, write this into your PS: `Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard`.
  - Paste the key into the DO dashboard.
- Click Create Droplet

> Copy the Droplet's IP address when it appears.

---
## Step 2 — SSH in and install Docker
- In your Droplet's console click on `Web Console`
- In the `Web Console` terminal enter:
```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose-plugin git
systemctl enable docker && systemctl start docker
```
- If errors occur, try this:
```bash
apt update && apt upgrade -y
apt install -y docker.io git
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
systemctl enable docker && systemctl start docker
```
> Verify it works: `docker-compose --version`

---
## Step 3 — Clone the repo
- In your Droplet's `Web Console`:
```bash
git clone https://github.com/<your-username>/<your-project-name>.git
cd <your-project-name>
```
---
## Step 4 — Generate SSL certificates
- Nginx requires these to start. Run the script already in your repo (Droplet's `Web Console`):
```bash
bash nginx/ssl/generate-certs.sh
```

> This creates nginx/ssl/cert.pem and nginx/ssl/key.pem (self-signed, valid 1 year). Your browser will show a security warning — click Advanced → Proceed.

---
## Step 5 — Create the .env file
- In your Droplet's `Web Console`:
```bash
cp .env.example .env # optional
nano .env
```

- Set these values (the rest can stay as defaults):
```bash
# Choose one: "openai" or "anthropic"
LLM_PROVIDER=gemini

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL =gpt-4-turbo-preview

ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_MODEL=gemini-2.5-flash-lite

DATABASE_URL=postgresql://postgres:postgres123@db:5432/<any_name>
DATABASE_ECHO=false

# Chroma Vector Store Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=course_materials

# Application Configuration
DEBUG=false
LOG_LEVEL=info

# Backend API Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://backend:8000

CORS_ORIGINS=https://<droplet-ip>

# Authentication & Security
# IMPORTANT: Generate a secure random secret key for production!
# You can generate one using: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=your_admin_password_here

SESSION_TIMEOUT_MINUTES=60
ACCESS_TOKEN_EXPIRE_DAYS=7

# Frontend Configuration
FRONTEND_HOST=localhost
FRONTEND_PORT=8501

POSTGRES_PASSWORD=<any_password:postgres123>
```
- Save with `Ctrl+O`, exit with `Ctrl+X`.

---
## Step 6 — Start everything
- `docker-compose up -d`
- Any problem, try this:
```bash
apt remove -y docker.io
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker
docker-compose up -d
```
> This builds and starts all four services in order: postgres → backend → frontend → nginx. The first run takes a few minutes to build the images.

Check status: `docker compose ps`

All should show health. Check logs if something is wrong:
- docker compose logs backend
- docker compose logs frontend

---
## Step 7 — Open the app

Go to `https://<droplet-ip>` in your browser. Accept the security warning (self-signed cert). The Streamlit UI should load.

The routing nginx handles:
- https://<droplet-ip>/ → Streamlit frontend
- https://<droplet-ip>/api/ → FastAPI backend
- https://<droplet-ip>/api/docs → API docs

> At this point you are running on a **self-signed certificate**, so the browser shows "Your connection is not private" (`NET::ERR_CERT_AUTHORITY_INVALID`) and you must click Advanced → Proceed. That is expected for testing, but **do not give this URL to students** — training users to click through security warnings is a bad habit, and the warning makes the app look broken. Step 8 replaces it with a trusted certificate.

---
## Step 8 — (Recommended) Use a domain + trusted SSL certificate

This removes the browser warning by replacing the self-signed cert with a free [Let's Encrypt](https://letsencrypt.org/) certificate. A trusted certificate requires a **hostname** — you cannot get one for a bare IP like `192.241.142.33`.

> **Note:** DigitalOcean does *not* sell domain names. It only offers free DNS hosting for a domain you already own (DO → Networking → Domains). You register the name elsewhere, or use a free option below.

### 8a — Pick a hostname

Choose one:

- **Free, no registration (fastest):** use [`nip.io`](https://nip.io). The hostname `192.241.142.33.nip.io` automatically resolves to your droplet IP — just substitute your own IP. Nothing to configure. Good enough for a thesis demo.
- **Free subdomain:** register one at [DuckDNS](https://www.duckdns.org) (e.g. `tutoria.duckdns.org`) and point it at your droplet IP.
- **Your own domain:** buy one (Porkbun, Namecheap, Cloudflare…), then add an `A` record pointing `tutoria.tudominio.com` → your droplet IP. You can manage that record for free in DO → Networking → Domains.

Set a shell variable so the rest of the steps are copy-paste (Droplet `Web Console`):
```bash
DOMAIN=192.241.142.33.nip.io   # replace with your chosen hostname
```

### 8b — Open port 80 and free it for issuance

Let's Encrypt validates over port 80. Make sure it's allowed (DO Cloud Firewall, if you use one, must permit 80/tcp), then stop nginx so certbot can bind to it:
```bash
docker compose stop nginx
```

### 8c — Issue the certificate

```bash
apt install -y certbot
certbot certonly --standalone -d "$DOMAIN" --agree-tos -m tu-correo@ejemplo.com --no-eff-email
```

Copy the freshly issued cert into the location nginx already expects (overwriting the self-signed ones from Step 4):
```bash
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem   nginx/ssl/key.pem
```
> No nginx config change is needed — `server_name _;` already accepts any hostname.

### 8d — Point the app at the hostname and bring it back up

Edit `.env` (`nano .env`) and change CORS to the hostname (HTTPS, no trailing slash):
```bash
CORS_ORIGINS=https://192.241.142.33.nip.io   # your $DOMAIN
```
Then restart:
```bash
docker compose up -d
```

Open `https://<your-domain>` — the padlock should now be clean, with no warning.

### 8e — Auto-renew (Let's Encrypt certs expire every 90 days)

Add a cron job that renews, copies the fresh certs, and reloads nginx. Run `crontab -e` and add (replace `$DOMAIN` and the repo path with your real values):
```cron
0 3 * * * certbot renew --quiet \
  --pre-hook  "docker compose -f /root/<your-project-name>/docker-compose.yml stop nginx" \
  --post-hook "cp /etc/letsencrypt/live/<your-domain>/fullchain.pem /root/<your-project-name>/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/<your-domain>/privkey.pem /root/<your-project-name>/nginx/ssl/key.pem && docker compose -f /root/<your-project-name>/docker-compose.yml up -d nginx"
```

---

## Additional steps
> Turn off the app:
> - docker-compose down
                                                                                                                                                                                    
> Turn back on the app:
> - `cd <your-project-name>`
> - docker-compose up -d

If you want to make changes to the app:
1. Make changes locally
2. git push from your local machine
3. In the Droplet console:
```bash
cd <you-project-name>
git pull
docker-compose up -d --build
```

Create Admin User. The backend should be running.
```bash
docker compose exec backend python -c "from init_db import create_admin_user; create_admin_user()"
```

The --build flag rebuilds the Docker images with your new code.

> Also, the app will automatically restart if the Droplet reboots, because all services have restart: unless-stopped in docker-compose.yml.