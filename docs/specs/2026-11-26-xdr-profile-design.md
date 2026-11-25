# Design Specification: Kamureii Endpoint Security & Detection Engineering GitHub Profile

- **Date:** 2026-11-26
- **Owner:** Tran Quoc Hung (`@kamureii`, VNPT Cyber Immunity, Hanoi)
- **Architecture:** Approach A — Split-Brain Monorepo (`worker/` Edge Sensor on Cloudflare Workers + D1, `generator/` Detection-as-Code Pipeline on GitHub Actions pushing pre-rendered SVGs to `generated-assets` branch)
- **Visual System (v3 Locked):** Sharp Tactical Obsidian & Crimson (`0px–2px` corners, zero bubbly AI rounding, `Bahnschrift` / `Space Grotesk` + `Cascadia Mono` / `JetBrains Mono`, high-contrast surface stepping `#08090C` → `#0B0D12` → `#13161E` → `#1B1F2B`, Crimson `#E52E3D` / `#FF5765` + Cobalt `#2563EB` / `#3B82F6` Offense↔Defense signal vector, reticle corner brackets, zero emojis)

---

## 1. Repository Layout

```text
kamureii/
├── README.md                                 # Profile landing page assembling live Worker SVGs + generated SVGs + Sigma Bio
├── profile.config.yml                        # Single source of truth (identity, Worker URL, enterprise MITRE coverage, links)
├── .gitignore
├── docs/
│   ├── specs/2026-11-26-xdr-profile-design.md
│   └── SETUP.md                              # Step-by-step Cloudflare D1 + Worker + GitHub Secrets guide
├── detections/
│   └── kamureii_identity.sigma.yml           # Syntax-validated Sigma bio rule
├── worker/                                   # Cloudflare Worker (TypeScript) + D1 SQLite
│   ├── package.json
│   ├── tsconfig.json
│   ├── wrangler.jsonc                        # Worker config, D1 binding, observability enabled
│   ├── migrations/
│   │   └── 0001_init.sql                     # counters + sliding_events tables (zero PII)
│   └── src/
│       ├── index.ts                          # Fetch handler & router
│       ├── types.ts                          # Env, TelemetrySnapshot, Scenario types
│       ├── telemetry.ts                      # D1 atomic writes, 60s sliding-window burst detector, Camo T1090 detection
│       ├── svg/
│       │   ├── theme.ts                      # Shared v3 Obsidian/Crimson tokens & XML escaper
│       │   ├── alertConsole.ts               # Live EDR Alert Console SVG (8/4 split, process lineage, 60s cadence trace, 2x2 KPI grid)
│       │   └── badges.ts                     # Sharp tactical action buttons & Canary counter SVG
│       └── pages/
│           └── detonation.ts                 # Interactive XDR Detonation Report HTML (displays request.cf live to visitor only, zero PII stored)
├── generator/                                # Python 3 Detection-as-Code SVG generator & hybrid scanner
│   ├── requirements.txt
│   ├── theme.py                              # Shared v3 Obsidian/Crimson SVG palette & helpers
│   ├── config_loader.py                      # Loads profile.config.yml & detections/kamureii_identity.sigma.yml
│   ├── scanner.py                            # Hybrid GitHub REST API scanner + enterprise coverage merger
│   ├── sigma_validator.py                    # Validates detections/kamureii_identity.sigma.yml against Sigma schema rules
│   ├── render_process_tree.py                # Renders assets/generated/process-tree.svg
│   ├── render_mitre_heatmap.py               # Renders assets/generated/mitre-heatmap.svg
│   ├── render_sysmon_feed.py                 # Renders assets/generated/sysmon-feed.svg
│   ├── render_sigma_card.py                  # Renders assets/generated/sigma-bio.svg (high-contrast recessed terminal card)
│   ├── render_alert_fallback.py              # Renders assets/generated/alert-fallback.svg (static v3 preview before Worker URL is configured)
│   ├── build_all.py                          # Orchestrator: scan -> validate -> render all SVGs -> sync README markers
│   └── tests/
│       └── test_generator.py                 # Unit tests for scanner, validator, XML validity, anti-XSS/anti-script guarantees
├── assets/
│   └── generated/                            # Locally previewable SVGs (CI pushes to orphan branch `generated-assets`)
└── .github/
    └── workflows/
        ├── update-telemetry.yml              # Cron 6h + push/manual: runs generator & updates `generated-assets` branch
        ├── validate-dac.yml                  # CI: validates Sigma bio + runs pytest + checks Worker TypeScript
        └── deploy-worker.yml                 # Auto-deploys Cloudflare Worker + applies D1 migrations on worker/ changes
```

---

## 2. Edge Sensor Architecture (`worker/`)

### Endpoints
| Route | Method | Cache Headers | Behavior |
|---|---|---|---|
| `/v1/alert.svg?theme=dark\|light` | `GET` | `no-cache, no-store, must-revalidate, max-age=0` + dynamic `ETag` | Records anonymous timestamp in D1 `sliding_events`, increments `visits` counter, evaluates 60s burst cadence + theme anomaly (`light` → `T1562`) + `github-camo` UA (`T1090`), returns `image/svg+xml` Live Edge Detection Console |
| `/v1/badge/canary.svg` | `GET` | `no-cache, no-store, must-revalidate, max-age=0` | Returns sharp tactical Canary counter & diagnostic trigger badge SVG |
| `/v1/badge/action.svg?kind=escalate\|benign\|isolate` | `GET` | `public, max-age=3600` | Returns sharp `0–2px` tactical response action button SVG matching v3 palette |
| `/v1/triage?action=benign\|escalate` | `GET` | `no-store` | Increments `benign` or `escalate` counter (with lightweight cookie throttle to prevent accidental double-counts), redirects `302` to GitHub profile (`benign`) or LinkedIn (`escalate`) |
| `/v1/canary` & `/v1/isolate` | `GET` | `no-store` | Increments `canary` counter in D1 (zero PII stored), serves standalone v3 **XDR Detonation Report** HTML page displaying visitor's own live `request.cf` metadata (TLS, HTTP version, Edge PoP, ASN, User-Agent) |
| `/health` | `GET` | `no-store` | JSON health check (`status`, `db_ok`, `timestamp`) |

### Privacy & Resilience Guarantees
- **Zero PII Stored:** D1 stores ONLY numeric counters (`visits`, `benign`, `escalate`, `canary`, `light_mode`) and anonymous integer epoch timestamps in `sliding_events` (auto-pruned after 10 minutes via `ctx.waitUntil`). No IPs, User-Agents, or fingerprints are ever persisted.
- **Deterministic Fallback:** If D1 is uninitialized or unavailable, `/v1/alert.svg` catches the error and renders a valid v3 SVG in `Degraded mode` (`Standby`) so GitHub never shows a broken image icon.
- **Burst Throttling:** When 60s request cadence exceeds 20 req/min, D1 still serves the `High · T1595` SVG while skipping extra `sliding_events` inserts to protect free-tier write quotas.

---

## 3. Detection-as-Code Pipeline (`generator/` & GitHub Actions)

- **Hybrid MITRE Scanner:** Fetches `kamureii`'s public repos, languages, stars, recent push events, repo topics (`t1xxx`), and Sigma/YARA/KQL artifacts via GitHub REST API (supports `GITHUB_TOKEN` in Actions and unauthenticated/offline fallback locally). Merges discovered public techniques with `enterprise_coverage` in `profile.config.yml`.
- **Sigma Bio Validation:** Validates required Sigma fields (`title`, `id`, `status`, `logsource`, `detection.condition`, `level`), verifies condition tokens reference declared selection blocks, and outputs CI validation status.
- **Visual Consistency across all SVGs:** Every generated SVG shares `generator/theme.py` (exact v3 hex palette `#08090C`, `#0B0D12`, `#13161E`, `#1B1F2B`, `#E52E3D`, `#FF5765`, `#2563EB`, `#3B82F6`, `0–2px` corners, `Bahnschrift`/`Space Grotesk` + `Cascadia Mono`/`JetBrains Mono`, zero emojis, zero `<script>` tags).
- **Clean `main` Branch:** `.github/workflows/update-telemetry.yml` pushes generated SVGs to an orphan `generated-assets` branch only when files change; `README.md` references them directly (and until `worker_url` is set in `profile.config.yml`, README cleanly falls back to the generated static alert console preview so the profile looks complete on day 1!).
