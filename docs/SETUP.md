# Setup & Deployment Guide — Kamureii XDR GitHub Profile

This repository works in **two progressive stages**:

1. **Stage 1 (Instant — GitHub Only):** Push `main` + `generated-assets`. Your profile immediately displays the v3 Obsidian & Crimson Header, Armed Edge Console, Process Lineage, Sigma Detection Bio, Hybrid MITRE ATT&CK Matrix, Sysmon Activity Stream, and Canary Artifact — auto-refreshed every 6 hours via GitHub Actions.
2. **Stage 2 (5 Minutes — Live Cloudflare Workers + D1):** Deploy `worker/` to activate real-time Visit Detection, GitHub Camo `T1090` detection, Light Mode `T1562` alert, 60s Burst `T1595` oscilloscope, clickable Triage buttons, and the Canary Detonation Report page.

---

## Stage 1: Push to GitHub (`kamureii/kamureii`)

```bash
git push -u origin main generated-assets
```

GitHub Actions (`Update XDR Telemetry SVGs` and `Detection-as-Code CI`) will run automatically on push.

---

## Stage 2: Activate Live Edge Detection (Cloudflare Workers + D1 — Free 100%)

You do **not** need Node.js installed locally — GitHub Actions can deploy everything automatically.

### Step 1: Create D1 Database on Cloudflare Dashboard
1. Open [Cloudflare Dashboard](https://dash.cloudflare.com) -> **Storage & Databases** -> **D1 SQL Database** -> **Create**.
2. Name the database **`kamureii-xdr-telemetry`**.
3. Copy the **Database ID** (UUID) and your **Account ID** (from the Workers & Pages overview sidebar).

### Step 2: Create a Cloudflare API Token
1. Go to **My Profile** -> **API Tokens** -> **Create Token**.
2. Use the **"Edit Cloudflare Workers"** template and add permission: **Account -> D1 -> Edit**.
3. Copy the generated API token.

### Step 3: Add 3 GitHub Repository Secrets
In `https://github.com/kamureii/kamureii/settings/secrets/actions`, add:
- `CLOUDFLARE_API_TOKEN` — token from Step 2
- `CLOUDFLARE_ACCOUNT_ID` — your Cloudflare Account ID
- `CLOUDFLARE_D1_DATABASE_ID` — UUID of `kamureii-xdr-telemetry`

### Step 4: Trigger Deploy
1. Open **Actions** -> **Deploy Cloudflare Edge Sensor** -> **Run workflow**.
2. GitHub Actions automatically applies `worker/migrations/0001_init.sql` to D1 and deploys `kamureii-xdr-edge`.
3. Copy the printed Worker URL (e.g., `https://kamureii-xdr-edge.<your-subdomain>.workers.dev`).

### Step 5: Connect Worker URL to Profile README
1. Edit `profile.config.yml` and paste your Worker URL into `edge.worker_url`:
   ```yaml
   edge:
     worker_url: https://kamureii-xdr-edge.<your-subdomain>.workers.dev
   ```
2. Regenerate `README.md` and push:
   ```bash
   python generator/build_all.py --sync-readme
   git add profile.config.yml README.md
   git commit -m "feat(edge): connect live Cloudflare XDR telemetry sensor"
   git push origin main
   ```

---

## Optional: Local Worker Development (if Node.js >= 20 is installed)

```bash
cd worker
npm install
npm run db:migrate:local
npm run dev
# Visit http://127.0.0.1:8787/v1/alert.svg?theme=dark
# Visit http://127.0.0.1:8787/v1/alert.svg?theme=light
# Visit http://127.0.0.1:8787/v1/canary
```

## Privacy Architecture
- D1 stores **only** numeric counters (`visits`, `benign`, `escalate`, `canary`, `light_mode`) and anonymous epoch timestamps in `sliding_events` (auto-pruned after 10 minutes).
- No visitor IP addresses, User-Agents, or browser fingerprints are ever logged or persisted.
- The `/v1/canary` and `/v1/isolate` pages reflect live Cloudflare Edge `request.cf` metadata back **exclusively to the requesting visitor** for educational EDR/Web telemetry demonstration.
