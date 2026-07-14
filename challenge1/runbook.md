# Challenge 1 Runbook: Docker Compose + EC2 Deployment

## Goal
Deploy the shared shopping list app on a single low-cost AWS EC2 instance while keeping the stack simple, secure, and within a modest budget.

## 1. Prerequisites
- An AWS account with access to EC2
- A registered domain name or a temporary public DNS name you can point at the instance
- Basic familiarity with SSH and Linux command-line usage
- Enough budget headroom to stay near the intended $100 AWS limit

## 2. Launch an EC2 instance
Use a budget-friendly Ubuntu 22.04 LTS instance:
- Instance type: `t3.micro` or `t3.small`
- Storage: at least 20 GiB
- Security group: allow inbound traffic on
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)

## 3. Connect to the instance
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 4. Install Docker and Docker Compose
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 curl git nginx
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

## 5. Clone the project and start the containers
```bash
git clone <your-repo-url>
cd capstone_sharedshoppinglist
docker compose up --build -d
```

If the app needs to be rebuilt later, rerun:
```bash
docker compose down
docker compose up --build -d
```

## 6. Configure Nginx as a reverse proxy
Create an Nginx site config that routes public traffic to the frontend container:
```bash
sudo tee /etc/nginx/sites-available/sharedshoppinglist <<'EOF'
server {
    listen 80;
    server_name your-domain.example.com;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/sharedshoppinglist /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

This sends browser traffic to the Vite frontend, which can communicate with the backend through the Docker network and the configured API URL.

## 7. Enable HTTPS with Let's Encrypt
Install Certbot and request a certificate:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.example.com
```

Certbot will also update the Nginx config for HTTPS and set up automatic renewal.

## 8. Verify the deployment
After DNS has propagated, test the public site:
```bash
curl -I http://your-domain.example.com
curl -I https://your-domain.example.com
```

Also verify the API endpoint:
```bash
curl https://your-domain.example.com/items
```

Expected result:
- The frontend loads successfully over HTTPS
- The API responds and the shopping list can be used

## 9. Cost and reliability notes
- A `t3.micro` or `t3.small` instance is usually sufficient for this small app
- Keep Docker containers running with `docker compose up -d` so the app survives reboots
- Consider using a persistent volume for PostgreSQL data so items remain available across restarts
