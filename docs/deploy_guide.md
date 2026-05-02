# Guide to deploying the app on DigitalOcean

## Step 1 — Create a Droplet
In DO dashboard → Droplets → Create Droplet:
- Image: Ubuntu 24.04 LTS
- Plan: Basic → Regular → $12/mo (2GB RAM, 1 vCPU)
- Region: nyc1
- Authentication: add your SSH key
  - In the PowerShell terminal enter: `ssh-keygen`
  - If you to store your key in a password-protected file, create a new file if not, press enter.
  - Create a password.
  - Copy the SSH key with: `Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard` in PowerShell.
  - Paste the key into the DO dashboard.
- Click Create Droplet

> Copy the Droplet's IP address when it appears.

---
## Step 2 — SSH in and install Docker
- In your Droplet's console click on `Web Console`
```bash
  ssh root@<droplet-ip>

  apt update && apt upgrade -y
  apt install -y docker.io docker-compose-plugin git
  systemctl enable docker && systemctl start docker
```

---
## Step 3 — Clone the repo

  git clone https://github.com/<your-username>/thesis-impl.git
  cd thesis-impl

---
## Step 4 — Generate SSL certificates

Nginx requires these to start. Run the script already in your repo:

bash nginx/ssl/generate-certs.sh

This creates nginx/ssl/cert.pem and nginx/ssl/key.pem (self-signed, valid 1 year). Your browser will show a security warning — just click Advanced → Proceed.

---
## Step 5 — Create the .env file

  cp .env.example .env
  nano .env

Set these values (the rest can stay as defaults):

  # Required — postgres container uses this
  POSTGRES_PASSWORD=choose_a_strong_password_here

  # Required — generate with:
  # python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  SECRET_KEY=paste_generated_key_here

  # Required — your Gemini API key
  GOOGLE_API_KEY=your_gemini_api_key_here

  # Production settings
  DEBUG=false
  CORS_ORIGINS=https://<droplet-ip>

  ▎ DATABASE_URL does not need to be set — docker-compose builds it automatically from POSTGRES_PASSWORD.

  Save with Ctrl+O, exit with Ctrl+X.

---
## Step 6 — Start everything
`docker compose up -d`

This builds and starts all four services in order: postgres → backend → frontend → nginx. The first run takes a few minutes to build the images.

Check status:
docker compose ps

All should show health. Check logs if something is wrong:
- docker compose logs backend
- docker compose logs frontend

---
## Step 7 — Open the app

Go to https://<droplet-ip> in your browser. Accept the security warning (self-signed cert). The Streamlit UI should load.

The routing nginx handles:
- https://<droplet-ip>/ → Streamlit frontend
- https://<droplet-ip>/api/ → FastAPI backend
- https://<droplet-ip>/api/docs → API docs

  ---
  That's it. If any step throws an error, paste the output here and we'll fix it.

Yes. The flow is:                                                                                                                                                                 
                                                                                                                                                                                    
1. Make changes locally                                                                                                                                                           
2. git push from your local machine
3. On the Droplet console:                                                                                                                                                        
  cd thesis-impl  
  git pull
  docker-compose up -d --build

The --build flag rebuilds the Docker images with your new code.

Turn off:                                                                                                                                                                         
docker-compose down
                                                                                                                                                                                    
Turn back on:   
docker-compose up -d

Also, the app will automatically restart if the Droplet reboots, because all services have restart: unless-stopped in docker-compose.yml.