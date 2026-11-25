import { renderDetonationHtml } from "./pages/detonation";
import { renderAlertConsoleSvg } from "./svg/alertConsole";
import { renderActionButtonSvg, renderCanaryBannerSvg } from "./svg/badges";
import { incrementCounter, parseTheme, readCounters, recordVisitAndBuildSnapshot } from "./telemetry";
import type { ActionKind } from "./types";

const NO_CACHE_SVG_HEADERS = {
  "Content-Type": "image/svg+xml; charset=utf-8",
  "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0, s-maxage=0",
  Pragma: "no-cache",
  Expires: "0",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
} as const;

const STATIC_SVG_HEADERS = {
  "Content-Type": "image/svg+xml; charset=utf-8",
  "Cache-Control": "public, max-age=3600",
  "X-Content-Type-Options": "nosniff",
} as const;

function parseThreshold(raw: string | undefined): number {
  const n = Number.parseInt(raw ?? "5", 10);
  return Number.isFinite(n) && n >= 2 ? n : 5;
}

function hasRecentTriageCookie(request: Request, action: string): boolean {
  const cookie = request.headers.get("cookie") ?? "";
  return cookie.includes(`kamureii_triage_${action}=1`);
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const username = env.GITHUB_USERNAME || "kamureii";
    const linkedinUrl = env.LINKEDIN_URL || "https://www.linkedin.com/in/kamureii/";
    const sensorName = env.SENSOR_NAME || "kamureii-xdr-edge.sys";
    const burstThreshold = parseThreshold(env.BURST_THRESHOLD);

    console.log(
      JSON.stringify({
        message: "edge request",
        method: request.method,
        path,
        hasTheme: url.searchParams.has("theme"),
      })
    );

    if (request.method !== "GET" && request.method !== "HEAD") {
      return Response.json({ error: "Method not allowed" }, { status: 405 });
    }

    // 1. Live Edge Detection Console SVG (Passive Visit + Burst + Theme + Camo T1090)
    if (path === "/v1/alert.svg") {
      const theme = parseTheme(url.searchParams.get("theme"));
      const snapshot = await recordVisitAndBuildSnapshot({
        db: env.TELEMETRY_DB,
        ctx,
        sensorName,
        username,
        theme,
        userAgent: request.headers.get("user-agent"),
        burstThreshold,
      });

      const svg = renderAlertConsoleSvg(snapshot);
      return new Response(svg, {
        status: 200,
        headers: {
          ...NO_CACHE_SVG_HEADERS,
          ETag: `"${crypto.randomUUID()}"`,
        },
      });
    }

    // 2. Live Canary Counter Banner SVG
    if (path === "/v1/badge/canary.svg") {
      try {
        const counters = await readCounters(env.TELEMETRY_DB);
        return new Response(renderCanaryBannerSvg(counters.canary, false), {
          status: 200,
          headers: {
            ...NO_CACHE_SVG_HEADERS,
            ETag: `"${crypto.randomUUID()}"`,
          },
        });
      } catch (err) {
        console.error(
          JSON.stringify({
            message: "canary badge D1 read failed",
            error: err instanceof Error ? err.message : String(err),
          })
        );
        return new Response(renderCanaryBannerSvg(0, true), {
          status: 200,
          headers: NO_CACHE_SVG_HEADERS,
        });
      }
    }

    // 3. Sharp Tactical Action Button SVGs
    if (path === "/v1/badge/action.svg") {
      const rawKind = url.searchParams.get("kind");
      const kind: ActionKind =
        rawKind === "escalate" || rawKind === "benign" || rawKind === "isolate" ? rawKind : "benign";
      return new Response(renderActionButtonSvg(kind), {
        status: 200,
        headers: STATIC_SVG_HEADERS,
      });
    }

    // 4. Interactive Triage Redirects (/v1/triage?action=benign|escalate)
    if (path === "/v1/triage") {
      const action = url.searchParams.get("action") === "escalate" ? "escalate" : "benign";
      const target = action === "escalate" ? linkedinUrl : `https://github.com/${username}`;

      const headers = new Headers({
        Location: target,
        "Cache-Control": "no-store",
        "Referrer-Policy": "no-referrer",
      });

      if (!hasRecentTriageCookie(request, action)) {
        try {
          await incrementCounter(env.TELEMETRY_DB, action);
          headers.append(
            "Set-Cookie",
            `kamureii_triage_${action}=1; Max-Age=600; Path=/v1/triage; HttpOnly; Secure; SameSite=Lax`
          );
        } catch (err) {
          console.error(
            JSON.stringify({
              message: "triage increment failed",
              action,
              error: err instanceof Error ? err.message : String(err),
            })
          );
        }
      }

      return new Response(null, { status: 302, headers });
    }

    // 5. Active Canary / Isolate Detonation Report Page
    if (path === "/v1/canary" || path === "/v1/isolate") {
      const source = path === "/v1/canary" ? "canary" : "isolate";
      let canaryCount = 0;
      try {
        canaryCount = await incrementCounter(env.TELEMETRY_DB, "canary");
      } catch (err) {
        console.error(
          JSON.stringify({
            message: "canary increment failed",
            error: err instanceof Error ? err.message : String(err),
          })
        );
      }

      const html = renderDetonationHtml({
        source,
        canaryCount,
        username,
        linkedinUrl,
        request,
      });

      return new Response(html, {
        status: 200,
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store",
          "X-Content-Type-Options": "nosniff",
          "Referrer-Policy": "no-referrer",
          "Content-Security-Policy":
            "default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none';",
        },
      });
    }

    // 6. Health Check
    if (path === "/health" || path === "/") {
      let dbOk = false;
      try {
        await env.TELEMETRY_DB.prepare("SELECT 1").first();
        dbOk = true;
      } catch {
        dbOk = false;
      }
      return Response.json(
        {
          sensor: sensorName,
          status: dbOk ? "online" : "degraded",
          db_ok: dbOk,
          timestamp: new Date().toISOString(),
        },
        { headers: { "Cache-Control": "no-store" } }
      );
    }

    return Response.json({ error: "Not found" }, { status: 404 });
  },
} satisfies ExportedHandler<Env>;
