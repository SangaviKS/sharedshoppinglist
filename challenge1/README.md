# Challenge 1: Production Foundations (Postgres & AWS Deployment)

## 1. The Engineering Concept
- Migrating from ephemeral container state to persistent multi-tier architectures.
- Frugal, secure production deployment within a rigid cloud credit envelope ($100 AWS limit).

## 2. The Chaos Simulation
The baseline code runs perfectly on your local laptop, but if you reboot your local machine, your data vanishes. Worse, if you copy this folder directly to a single AWS cloud instance and drop it inside a background process, the app will instantly break because it has no reverse proxy, public routing layer, or persistent storage configuration.

### How to Run the Chaos Test:
1. Spin up the intern's base application.
2. Add three items to the list via your browser.
3. Force-kill the backend process in your terminal (`Ctrl + C`).
4. Restart the backend process and refresh your browser.
5. **What happens:** The list is completely empty. The storage layer was tied to volatile process memory.

## 3. Your Task
You must move the app to a production-ready containerized footprint and deploy it live.
1. Use Claude to write a `docker-compose.yml` file that orchestrates three services: a Python FastAPI service, a React frontend compiled via Vite, and an official PostgreSQL container. Use a named Docker volume to ensure database data persists across restarts.
2. Instruct Claude to write a deployment runbook targeting a single AWS EC2 instance (e.g., a `t3.micro` or `t3.small` instance to stay safely inside the $100 budget). 
3. The deployment guide must instruct how to set up an incoming Nginx reverse proxy or basic application router, map a public domain name, and configure Let's Encrypt for automated HTTPS/SSL certificate renewals.
