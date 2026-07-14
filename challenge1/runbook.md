# Challenge 1 Runbook: Deploying to a Single AWS EC2 Instance

Target: one `t3.micro` (or `t3.small` if you need more headroom) EC2 instance
running Docker Compose (Postgres + FastAPI backend + compiled React
frontend), fronted by Nginx with a free Let's Encrypt certificate.

Estimated cost: a `t3.micro` on-demand is ~$0.0104/hr (~$7.50/month) in
`us-east-1`, or **$0/month** if your account is still in the 12-month Free
Tier (750 hrs/month of `t3.micro` included). A 20 GiB gp3 EBS volume adds
~$1.60/month. Well inside the $100 budget even run continuously for the
whole challenge — see [§10](#10-cost--budget-guardrails) for how to make sure
you don't leave anything running by accident.

## Architecture

```
Browser
  │  HTTPS (443) / HTTP→HTTPS redirect (80)
  ▼
Nginx (host process, not containerized)
  │
  ├─ "/"           → frontend container  (127.0.0.1:8080 → nginx:alpine serving Vite build)
  └─ "/items..."   → backend container   (127.0.0.1:8000 → FastAPI/uvicorn)
                          │
                          ▼
                     db container (Postgres, no host port — internal only)
```

Only ports 22, 80, and 443 are ever open to the internet. The app
containers bind to `127.0.0.1` only, so they're unreachable from outside the
box even if you forget the security group rule.

---

## 1. Prerequisites

- An AWS account (yours: account `185188589247`, region default `us-east-1`)
- A GitHub account to host this repo (see §2)
- Optional: a domain name you control. If you don't have one, use a free
  wildcard DNS service like `nip.io` — see §5.

## 2. Push this project to GitHub

The project was just initialized as a git repo locally and given an initial
commit. Push it to GitHub so the EC2 instance can `git clone` it:

1. Go to https://github.com/new and create a new repository (e.g.
   `sharedshoppinglist`). Don't initialize it with a README — this project
   already has one. Public or private both work; this deployment used a
   **public** repo (`https://github.com/SangaviKS/sharedshoppinglist`) —
   `.env` is git-ignored, so no secrets end up in it either way.
2. Back in your terminal:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```
3. If your repo is private and you're prompted for credentials, use a
   [personal access token](https://github.com/settings/tokens) instead of
   your password (GitHub no longer accepts password auth over HTTPS). Public
   repos need no auth to clone.

Your `.env` file (with real secrets) is git-ignored and will **not** be
pushed — you'll create it directly on the server in §8. `.env.example`
documents the variables it needs.

## 3. Launch the EC2 instance (AWS Console)

1. Sign in to the [AWS Console](https://console.aws.amazon.com/ec2/) and
   make sure you're in your intended region (top-right region selector).
2. Go to **EC2 → Instances → Launch instance**.
3. **Name**: `sharedshoppinglist`.
4. **AMI**: Ubuntu Server 26.04 LTS (Free Tier eligible).
5. **Instance type**: `t3.micro` (Free Tier eligible) — bump to `t3.small`
   only if you see the backend/frontend build steps getting OOM-killed.
6. **Key pair**: click **Create new key pair**, name it (e.g.
   `sharedshoppinglist-key`), type RSA, format `.pem`. Download it — this is
   the only time you'll get it. Move it somewhere safe, e.g.:
   ```bash
   mkdir -p ~/.ssh
   mv ~/Downloads/sharedshoppinglist-key.pem ~/.ssh/
   chmod 400 ~/.ssh/sharedshoppinglist-key.pem
   ```
7. **Network settings → Edit**:
   - Create a new security group named `sharedshoppinglist-sg`.
   - Allow: SSH (22) from **My IP 70.178.191.177/32** (not `0.0.0.0/0` — no reason to expose
     SSH to the whole internet), HTTP (80) from Anywhere, HTTPS (443) from
     Anywhere.
8. **Configure storage**: 20 GiB, gp3.
9. Click **Launch instance**.

### Attach an Elastic IP (so the address doesn't change on reboot)

1. **EC2 → Network & Security → Elastic IPs → Allocate Elastic IP address**.
2. Allocate it, then **Actions → Associate Elastic IP address**, and pick
   your `sharedshoppinglist` instance.
3. Note this Elastic IP address: 3.227.138.40 — it's what you'll SSH to and point DNS at.

> Budget note: an Elastic IP is free *while associated with a running
> instance*. It starts costing money if you stop the instance but keep the
> IP allocated, or if you allocate one and never associate it. Release it in
> §10 if you tear the instance down.

## 4. Connect to the instance

```bash
ssh -i ~/.ssh/sharedshoppinglist-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

(The `.pem` doesn't have to live in `~/.ssh` — any path works, e.g. this
deployment kept it under a personal `AWS-Account` folder instead. Whatever
the path, `chmod 400` it and point `-i` at it.)

The first connection to a new IP will show a host-key prompt
(`The authenticity of host '...' can't be established`) — this is normal
for any brand-new SSH destination, not an error. Type `yes` to trust it.

## 5. Point a domain at the instance

**If you own a domain**, add an `A` record at your registrar/DNS provider
pointing to your Elastic IP (e.g. `shoppinglist.yourdomain.com → <IP>`).
Propagation is usually minutes, occasionally up to ~30 min.

**If you don't have a domain**, use a free wildcard DNS service instead —
no signup needed. Given Elastic IP `203.0.113.10`, the hostname
`203-0-113-10.nip.io` automatically resolves to `203.0.113.10`. Use that as
your "domain" everywhere below (Nginx `server_name`, Certbot `-d` flag, and
`VITE_API_URL`). Let's Encrypt can issue real certificates for it since it's
publicly resolvable DNS.

This deployment used Elastic IP `3.227.138.40` → `3-227-138-40.nip.io`,
confirmed resolving correctly with `dig +short 3-227-138-40.nip.io` before
relying on it.

## 6. Install Docker, Docker Compose, and Nginx

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 nginx git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

## 7. Clone the repo

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

(For a private repo, you'll be prompted for your GitHub username and a
personal access token. Public repos, like the one used for this deployment,
clone with no auth prompt.)

## 8. Create the production `.env`

```bash
cp .env.example .env
nano .env
```

Set real values:
```bash
POSTGRES_DB=shoppinglist
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<generate a strong password, e.g. `openssl rand -hex 24` — avoid -base64 here since it can include / and + which break the DATABASE_URL below>
VITE_API_URL=https://shoppinglist.yourdomain.com   # or https://203-0-113-10.nip.io
```

`VITE_API_URL` is baked into the frontend at build time and must be the
**same origin** you'll serve the site from over HTTPS — the frontend and
API share one domain, split by path at the Nginx layer (see §9), so there's
no CORS to worry about.

## 9. Build and start the stack

```bash
docker compose up --build -d
docker compose ps
```

All three containers should show as running/healthy. The `db` container has
no host port; `backend` and `frontend` are bound to `127.0.0.1` only, so
nothing is publicly reachable yet — that's expected until Nginx is wired up
next.

Sanity check from the instance itself:
```bash
curl http://127.0.0.1:8000/items
curl -I http://127.0.0.1:8080/
```

## 10. Configure the host Nginx reverse proxy

```bash
sudo tee /etc/nginx/sites-available/sharedshoppinglist <<'EOF'
server {
    listen 80;
    server_name shoppinglist.yourdomain.com;   # or 203-0-113-10.nip.io

    location ~ ^/(items)(/.*)?$ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/sharedshoppinglist /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

The `location ~ ^/(items)(/.*)?$` block matches this API's known routes
(`/items`, `/items/{id}`, `/items/{id}/complete`) and sends only those to
the backend; everything else falls through to the compiled frontend. If you
add new API routes later under a different path, add them to that regex (or
switch the backend to mount all routes under `/api` and adjust the regex to
`^/api/`).

Test over plain HTTP before adding TLS:
```bash
curl -I http://shoppinglist.yourdomain.com/
curl http://shoppinglist.yourdomain.com/items
```

## 11. Enable HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d shoppinglist.yourdomain.com
```

Certbot rewrites the Nginx config to redirect HTTP → HTTPS and installs a
systemd timer (`certbot.timer`) that renews automatically before the
90-day certificate expires — nothing to do manually. Verify the timer:

```bash
systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

## 12. Verify the deployment end to end

```bash
curl -I https://shoppinglist.yourdomain.com/
curl https://shoppinglist.yourdomain.com/items
```

Then in a browser, open `https://shoppinglist.yourdomain.com`, add a few
items, and confirm they persist. To confirm the persistence goal of
Challenge 1 is actually met on this deployment:

```bash
docker compose restart backend
```
Refresh the browser — items should still be there (stored in the `db`
container's named volume, not backend process memory).

## 13. Cost & budget guardrails

- Check spend anytime: **AWS Console → Billing → Cost Explorer**, or set a
  [Budget alert](https://console.aws.amazon.com/billing/home#/budgets) at,
  say, $20 so you get an email well before the $100 ceiling. (This
  deployment set the alert at $1 — an even earlier tripwire, since any
  billable activity at all triggers it well ahead of the $100 limit.)
- To pause spend without losing your setup: **stop** (don't terminate) the
  instance from the EC2 console. EBS storage still bills (~$0.08/GiB-month,
  so ~$1.60/month for 20 GiB) but compute stops billing.
- If you stop the instance, either release the Elastic IP or expect a small
  hourly charge for an EIP not attached to a running instance.
- To fully tear down when you're done with the challenge: terminate the
  instance, then delete the Elastic IP allocation and the security group.

## 14. Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `nginx -t` fails after Certbot | `server_name` mismatch between DNS and config | Confirm `dig +short shoppinglist.yourdomain.com` returns your Elastic IP |
| Browser gets a connection refused on 80/443 | Security group missing the rule | Re-check §3 step 7 inbound rules |
| Frontend loads but "Add" does nothing | `VITE_API_URL` wrong at build time | Fix `.env`, then `docker compose up --build -d frontend` to rebuild |
| Items vanish after `docker compose down` | Used `down -v` (deletes volumes) | Use `docker compose down` (no `-v`) or `docker compose restart` |
| `git clone` on the instance asks for a password | HTTPS + no PAT configured | Use a GitHub personal access token, or switch the remote to SSH with a deploy key |

## 15. Deployment record

This runbook was executed end to end on a live AWS account, not just
drafted. Summary of the actual run:

- **Instance**: `t3.micro`, Ubuntu 26.04 LTS, `us-east-1`, Elastic IP
  `3.227.138.40`
- **Domain**: `3-227-138-40.nip.io` (no owned domain needed)
- **Repo**: `https://github.com/SangaviKS/sharedshoppinglist` (public)
- **HTTPS**: Let's Encrypt certificate issued via Certbot, expires
  2026-10-12, auto-renewal via `certbot.timer`
- **Budget alert**: set at $1
- **Verification performed**:
  - `docker compose ps` — all three containers (`db`, `backend`,
    `frontend`) up and healthy
  - `curl` checks against `127.0.0.1:8000` and `127.0.0.1:8080` from the
    instance, then against `http://3-227-138-40.nip.io` and
    `https://3-227-138-40.nip.io` from outside — all returned expected
    responses
  - Added an item through the live browser UI at
    `https://3-227-138-40.nip.io`, ran `docker compose restart backend`,
    and confirmed the item was still present afterward — the Challenge 1
    persistence requirement holds on the real deployment, not just locally
