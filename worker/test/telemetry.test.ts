import { describe, expect, it } from "vitest";
import { renderAlertConsoleSvg } from "../src/svg/alertConsole";
import { renderActionButtonSvg, renderCanaryBannerSvg } from "../src/svg/badges";
import {
  buildCadenceBuckets,
  buildDegradedSnapshot,
  classifyDetection,
  detectCamoProxy,
} from "../src/telemetry";

describe("Kamureii Edge Telemetry Logic", () => {
  it("flags github-camo proxy requests under T1090", () => {
    const res = detectCamoProxy("github-camo (abc123)");
    expect(res.viaCamo).toBe(true);
    expect(res.proxyLabel).toBe("camo.githubusercontent.com");
  });

  it("escalates Light Mode visitors to CRITICAL T1562", () => {
    const res = classifyDetection({
      theme: "light",
      burstCount60s: 1,
      burstThreshold: 5,
      viaCamo: true,
    });
    expect(res.severity).toBe("CRITICAL");
    expect(res.severityBadge).toContain("T1562");
    expect(res.posture).toBe("Critical");
  });

  it("escalates rapid requests exceeding threshold to HIGH T1595", () => {
    const res = classifyDetection({
      theme: "dark",
      burstCount60s: 7,
      burstThreshold: 5,
      viaCamo: true,
    });
    expect(res.severity).toBe("HIGH");
    expect(res.severityBadge).toContain("T1595");
    expect(res.posture).toBe("Elevated");
  });

  it("buckets 60-second timestamps cleanly across 8 intervals", () => {
    const now = 1_700_000_060;
    const buckets = buildCadenceBuckets([now - 55, now - 54, now - 2, now], now);
    expect(buckets).toHaveLength(8);
    expect(buckets[0]).toBe(2);
    expect(buckets[7]).toBe(2);
  });

  it("renders valid, script-free v3 SVGs for degraded fallback and badges", () => {
    const snap = buildDegradedSnapshot({
      sensorName: "kamureii-xdr-edge.sys",
      username: "kamureii",
      theme: "dark",
      viaCamo: true,
      proxyLabel: "camo.githubusercontent.com",
      burstThreshold: 5,
    });
    const alertSvg = renderAlertConsoleSvg(snap);
    expect(alertSvg).toContain("<svg");
    expect(alertSvg).toContain("Degraded mode");
    expect(alertSvg).not.toContain("<script");

    const canarySvg = renderCanaryBannerSvg(23, false);
    expect(canarySvg).toContain("km_edr_unhook_poc_v2.dmp.enc");
    expect(canarySvg).toContain("23 times");

    const actionSvg = renderActionButtonSvg("escalate");
    expect(actionSvg).toContain("Escalate to Tier 2");
  });
});
