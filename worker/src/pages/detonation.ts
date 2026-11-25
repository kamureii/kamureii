import { escXml, formatUtcTimestamp, V3_THEME as T } from "../svg/theme";

interface DetonationPageParams {
  source: "canary" | "isolate";
  canaryCount: number;
  username: string;
  linkedinUrl: string;
  request: Request;
}

export function renderDetonationHtml(params: DetonationPageParams): string {
  const cf = (params.request as Request & { cf?: Record<string, unknown> }).cf ?? {};
  const tlsVersion = String(cf.tlsVersion ?? "TLSv1.3");
  const httpProtocol = String(cf.httpProtocol ?? "HTTP/2");
  const colo = String(cf.colo ?? "EDGE");
  const country = String(cf.country ?? "Unknown");
  const city = String(cf.city ?? "Masked");
  const asn = cf.asn ? `AS${String(cf.asn)}` : "Unavailable";
  const asOrg = String(cf.asOrganization ?? "Unknown network");
  const userAgent = params.request.headers.get("user-agent") ?? "Not supplied";
  const acceptLang = params.request.headers.get("accept-language")?.split(",")[0] ?? "Not supplied";
  const nowUtc = formatUtcTimestamp(new Date());

  const isCanary = params.source === "canary";
  const heading = isCanary ? "Canary token triggered" : "Active edge telemetry inspection";
  const badge = isCanary ? "T1552 · Unsecured Credentials Lure" : "Active Opt-In Sensor Check";
  const intro = isCanary
    ? "You accessed the diagnostic symbol lure on Kamureii's GitHub profile. Curiosity is the core instinct of a security engineer. Below is what an active edge sensor observes when you click an external link — rendered strictly to your session and never stored in D1."
    : "Passive GitHub README images pass through github-camo, hiding client telemetry behind MITRE T1090 proxy behavior. By opting in to this direct edge endpoint, you can inspect the real transport metadata visible at Cloudflare Edge — zero PII is stored.";

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escXml(heading)} — Kamureii XDR Edge</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100dvh;
      background-color: ${T.voidBg};
      background-image: radial-gradient(rgba(255,255,255,0.045) 1px, transparent 1px);
      background-size: 24px 24px;
      color: ${T.textPrimary};
      font-family: 'Space Grotesk', 'Bahnschrift', 'DIN Alternate', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .frame {
      width: 100%;
      max-width: 720px;
      background: ${T.slabBg};
      border: 1px solid ${T.borderStrong};
      position: relative;
    }
    .frame::before, .frame::after {
      content: "";
      position: absolute;
      width: 10px;
      height: 10px;
      pointer-events: none;
    }
    .frame::before {
      bottom: -1px; left: -1px;
      border-bottom: 2px solid ${T.crimson};
      border-left: 2px solid ${T.crimson};
    }
    .frame::after {
      bottom: -1px; right: -1px;
      border-bottom: 2px solid ${T.cobaltBright};
      border-right: 2px solid ${T.cobaltBright};
    }
    .signal {
      height: 3px;
      background: linear-gradient(90deg, ${T.crimson} 0%, ${T.crimsonMid} 48%, ${T.cobalt} 100%);
    }
    .inner { padding: 28px; display: grid; gap: 20px; }
    .meta {
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;
      padding-bottom: 14px; border-bottom: 1px solid ${T.borderBase};
      font-family: 'JetBrains Mono', 'Cascadia Mono', monospace; font-size: 12px;
    }
    .tag {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 3px 8px; background: ${T.kpiCrimsonBg}; border: 1px solid ${T.crimsonBorder}; color: ${T.crimsonInk};
    }
    .diode { width: 7px; height: 7px; background: ${T.crimson}; display: inline-block; }
    h1 { margin: 0; font-size: 28px; line-height: 1.15; letter-spacing: -0.02em; font-weight: 600; }
    p { margin: 0; color: ${T.textSecondary}; font-size: 14px; line-height: 1.65; max-width: 64ch; }
    .well {
      background: ${T.recessedBg};
      border: 1px solid ${T.borderBase};
      font-family: 'JetBrains Mono', 'Cascadia Mono', monospace;
      font-size: 12px;
      font-variant-numeric: tabular-nums;
    }
    .well-head {
      padding: 10px 16px;
      background: ${T.headerBg};
      border-bottom: 1px solid ${T.borderBase};
      display: flex; justify-content: space-between; color: ${T.textSecondary};
    }
    .row {
      padding: 11px 16px;
      display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px;
      border-top: 1px solid ${T.borderSubtle};
    }
    .row.first { border-top: none; }
    .row.audit { background: #1E0E13; }
    .k { color: ${T.textMuted}; }
    .v { color: ${T.textPrimary}; text-align: right; word-break: break-all; max-width: 440px; }
    .v.blue { color: ${T.cobaltInk}; }
    .v.red { color: ${T.crimsonInk}; }
    .actions { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; padding-top: 6px; }
    .btn-group { display: flex; flex-wrap: wrap; gap: 8px; }
    .btn {
      display: inline-flex; align-items: center; gap: 8px;
      height: 38px; padding: 0 16px; border-radius: 2px;
      font-family: 'JetBrains Mono', 'Cascadia Mono', monospace; font-size: 12px;
      text-decoration: none; cursor: pointer;
      transition: background-color 150ms cubic-bezier(0.22,1,0.36,1), transform 150ms;
    }
    .btn:active { transform: translateY(1px); }
    .btn-primary { background: ${T.crimson}; color: #F8FAFC; border: 1px solid ${T.crimson}; }
    .btn-primary:hover { background: #F03E4D; }
    .btn-secondary { background: ${T.headerBg}; color: ${T.textPrimary}; border: 1px solid ${T.borderStrong}; }
    .btn-secondary:hover { background: #232938; }
    .count { font-family: 'JetBrains Mono', 'Cascadia Mono', monospace; font-size: 12px; color: ${T.textMuted}; }
  </style>
</head>
<body>
  <main class="frame">
    <div class="signal"></div>
    <div class="inner">
      <div class="meta">
        <span class="tag"><span class="diode"></span>${escXml(badge)}</span>
        <span style="color:${T.textMuted}">${escXml(nowUtc)}</span>
      </div>

      <div>
        <h1>${escXml(heading)}</h1>
        <p style="margin-top:10px">${escXml(intro)}</p>
      </div>

      <section class="well" aria-label="Observed edge telemetry">
        <div class="well-head">
          <span>Ephemeral transport telemetry (visible only to you)</span>
          <span>Cloudflare Edge</span>
        </div>
        <div class="row first"><span class="k">Transport</span><span class="v">${escXml(tlsVersion)} · ${escXml(httpProtocol)}</span></div>
        <div class="row"><span class="k">Edge PoP / Region</span><span class="v blue">${escXml(colo)} · ${escXml(city)}, ${escXml(country)}</span></div>
        <div class="row"><span class="k">Network ASN</span><span class="v">${escXml(asn)} · ${escXml(asOrg)}</span></div>
        <div class="row"><span class="k">Locale</span><span class="v">${escXml(acceptLang)}</span></div>
        <div class="row"><span class="k">User-Agent</span><span class="v">${escXml(userAgent)}</span></div>
        <div class="row audit"><span class="k" style="color:${T.crimsonSub}">PII persistence</span><span class="v red">None — only anonymous counter incremented</span></div>
      </section>

      <div class="actions">
        <span class="count">Total canary / inspection hits: <strong style="color:${T.textPrimary}">${params.canaryCount}</strong></span>
        <div class="btn-group">
          <a class="btn btn-secondary" href="https://github.com/${escXml(params.username)}">Return to GitHub profile</a>
          <a class="btn btn-primary" href="${escXml(params.linkedinUrl)}" rel="noopener noreferrer">Connect on LinkedIn</a>
        </div>
      </div>
    </div>
  </main>
</body>
</html>`;
}
